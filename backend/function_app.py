import json
import logging
import os
import uuid

import pyodbc
import requests
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@app.route(route="analyze", methods=["POST"])
def analyze(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("analyze 요청 수신")

    content_type = req.headers.get("Content-Type", "")
    
    if "multipart/form-data" in content_type:
        visibility = req.form.get("visibility", "private")
        if visibility not in ("public", "private"):
            visibility = "private"
        try:
            if "file" not in req.files:
                return func.HttpResponse(
                    json.dumps({"error": "Missing 'file' in form-data"}),
                    status_code=400,
                    mimetype="application/json",
                )

            image_data = req.files["file"].read()

            blob_name = f"{uuid.uuid4()}.jpg"
            blob_service = BlobServiceClient.from_connection_string(os.environ["BLOB_CONNECTION_STRING"])
            blob_client = blob_service.get_blob_client(container=os.environ["BLOB_CONTAINER_NAME"], blob=blob_name)
            blob_client.upload_blob(image_data, overwrite=True)

            vision_client = ImageAnalysisClient(
                endpoint=os.environ["AZURE_VISION_ENDPOINT"],
                credential=AzureKeyCredential(os.environ["AZURE_VISION_KEY"]),
            )
            ocr_result = vision_client.analyze(image_data=image_data, visual_features=[VisualFeatures.READ])

            input_type = "image"
            blob_url = blob_client.url
            text = " ".join(line.text for block in ocr_result.read.blocks for line in block.lines)
        except Exception as e:
            logging.error(f"Image processing error: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Image processing failed"}),
                status_code=500,
                mimetype="application/json",
            )

    else:
        try:
            body = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Invalid JSON"}),
                status_code=400,
                mimetype="application/json",
            )

        if body is None or "text" not in body:
            return func.HttpResponse(
                json.dumps({"error": "Missing 'text' field"}),
                status_code=400,
                mimetype="application/json",
            )

        input_type = "text"
        blob_url = None
        text = body["text"]
        visibility = body.get("visibility", "private")
        if visibility not in ("public", "private"):
            visibility = "private"

    if not text.strip():
        return func.HttpResponse(
            json.dumps({"error": "Text cannot be empty"}),
            status_code=400,
            mimetype="application/json",
        )

    # 파트 B 호출 (Container App 배포 후 아래 mock 코드를 실제 호출로 교체)
    request_id = str(uuid.uuid4())

    try:
        response = requests.post(
            f"{os.environ['CONTAINER_APP_URL']}/analyze",
            json={"request_id": request_id, "text": text},
            timeout=30
        )
        response.raise_for_status()
        b_result = response.json()
        label = b_result["label"]
        risk_level = b_result["risk_level"]
        confidence = b_result["confidence"]
        reason = b_result["reason"]
    except Exception as e:
        logging.error(f"Part B call failed: {e}")
        return func.HttpResponse(
            json.dumps({"error": "AI analysis failed"}),
            status_code=500,
            mimetype="application/json",
        )
    if visibility == "public":
        try:
            conn = pyodbc.connect(os.environ["SQL_CONNECTION_STRING"])
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO analyses (input_type, original_text, blob_url, label, confidence, reason, risk_level, visibility)
                OUTPUT INSERTED.id
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                input_type, text, blob_url, label, confidence, json.dumps(reason), risk_level, visibility,
            )
            record_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
        except Exception as e:
            logging.error(f"SQL error: {e}")
            return func.HttpResponse(
                json.dumps({"error": "Database error"}),
                status_code=500,
                mimetype="application/json",
            )

    return func.HttpResponse(
        json.dumps(
            {"input_type": input_type, "label": label, "risk_level": risk_level, "confidence": confidence, "reason": reason},
            ensure_ascii=False,
        ),
        mimetype="application/json",
        status_code=200,
    )


@app.route(route="history", methods=["GET"])
def history(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("history 요청 수신")

    try:
        limit = min(int(req.params.get("limit", "20")), 100)
        offset = int(req.params.get("offset", "0"))
    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "limit and offset must be integers"}),
            status_code=400,
            mimetype="application/json",
        )

    try:
        conn = pyodbc.connect(os.environ["SQL_CONNECTION_STRING"])
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, input_type, original_text, label, risk_level, confidence, reason, visibility, created_at
            FROM analyses
            ORDER BY created_at DESC
            OFFSET ? ROWS FETCH NEXT ? ROWS ONLY
            """,
            offset, limit,
        )
        rows = cursor.fetchall()
        columns = [col[0] for col in cursor.description]

        cursor.execute("SELECT COUNT(*) FROM analyses")
        total = cursor.fetchone()[0]
        conn.close()

        items = [dict(zip(columns, row)) for row in rows]
        for item in items:
            item["reason"] = json.loads(item["reason"] or "[]")

    except Exception as e:
        logging.error(f"SQL error: {e}")
        return func.HttpResponse(
            json.dumps({"error": "Database error"}),
            status_code=500,
            mimetype="application/json",
        )

    return func.HttpResponse(
        json.dumps({"items": items, "total": total}, ensure_ascii=False, default=str),
        mimetype="application/json",
        status_code=200,
    )
