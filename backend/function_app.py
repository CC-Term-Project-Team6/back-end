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

    if not text.strip():
        return func.HttpResponse(
            json.dumps({"error": "Text cannot be empty"}),
            status_code=400,
            mimetype="application/json",
        )

    # 파트 B 호출 (Container App 배포 후 아래 mock 코드를 실제 호출로 교체)
    result = "normal"
    confidence = 0.0
    reasons = []

    try:
        conn = pyodbc.connect(os.environ["SQL_CONNECTION_STRING"])
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO analyses (input_type, original_text, blob_url, result, confidence, reasons)
            OUTPUT INSERTED.id
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            input_type, text, blob_url, result, confidence, json.dumps(reasons),
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
            {"id": record_id, "input_type": input_type, "result": result, "confidence": confidence, "reasons": reasons},
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
            SELECT id, input_type, original_text, result, confidence, reasons, created_at
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
            item["reasons"] = json.loads(item["reasons"] or "[]")

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
