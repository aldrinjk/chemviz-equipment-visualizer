# backend/api/views.py
import json
import pandas as pd  # NEW: to build raw rows from uploaded CSV

from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from django.http import FileResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import authentication_classes, permission_classes

from .models import Dataset
from .serializers import DatasetSerializer  # noqa: F401 (kept for later use)
from .services import compute_summary


@api_view(['GET'])
def health(request):
    return Response({"status": "ok"})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_csv(request):
    """
    Multipart form-data:
      file: <CSV file>
    """
    if 'file' not in request.FILES:
        return Response(
            {"detail": "No file provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    csv_file = request.FILES['file']
    try:
        # 1) Compute summary (uses the uploaded file)
        summary = compute_summary(csv_file)

        # 2) Build raw rows (first reset pointer so pandas can read)
        csv_file.seek(0)
        df = pd.read_csv(csv_file)
        records = df.to_dict(orient="records")

        # 3) Create Dataset (NO csv_file field; we store summary + raw_data)
        ds = Dataset.objects.create(
            name=csv_file.name,
            uploaded_at=timezone.now(),
            summary=summary,
            raw_data=records,  # NEW: save raw rows into JSONField
        )

        # 4) Keep only last 5 datasets
        qs = Dataset.objects.order_by('-uploaded_at')
        if qs.count() > 5:
            for old in qs[5:]:
                old.delete()

        data = {
            "dataset_id": ds.id,
            "filename": ds.name,
            "uploaded_at": ds.uploaded_at,
            **summary,
        }
        return Response(data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response(
            {"detail": str(e)},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(['GET'])
def summary_latest(request):
    ds = Dataset.objects.order_by('-uploaded_at').first()
    if not ds:
        return Response(
            {"detail": "No datasets yet."},
            status=status.HTTP_404_NOT_FOUND,
        )
    data = {
        "dataset_id": ds.id,
        "filename": ds.name,
        "uploaded_at": ds.uploaded_at,
        **ds.summary,
    }
    return Response(data)


@api_view(['GET'])
def history(request):
    qs = Dataset.objects.order_by('-uploaded_at')[:5]
    items = [{
        "dataset_id": ds.id,
        "filename": ds.name,
        "uploaded_at": ds.uploaded_at,
        "summary": ds.summary,
    } for ds in qs]
    return Response({"items": items})


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def report_latest(request):
    """
    Generate a simple PDF report for the latest dataset.
    """
    ds = Dataset.objects.order_by('-uploaded_at').first()
    if not ds:
        return Response(
            {"detail": "No datasets yet."},
            status=status.HTTP_404_NOT_FOUND,
        )

    buf = BytesIO()
    p = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    y = height - 50
    p.setFont("Helvetica-Bold", 16)
    p.drawString(50, y, "Chemical Equipment Report (Latest Dataset)")
    y -= 40

    p.setFont("Helvetica", 11)
    p.drawString(50, y, f"File: {ds.name}")
    y -= 20
    p.drawString(50, y, f"Uploaded At: {ds.uploaded_at}")
    y -= 30

    summary = ds.summary or {}
    total = summary.get("total_count", "N/A")
    av = summary.get("averages", {})
    dist = summary.get("type_distribution", {})

    p.drawString(50, y, f"Total Rows: {total}")
    y -= 20
    p.drawString(50, y, f"Avg Flowrate: {av.get('Flowrate')}")
    y -= 20
    p.drawString(50, y, f"Avg Pressure: {av.get('Pressure')}")
    y -= 20
    p.drawString(50, y, f"Avg Temperature: {av.get('Temperature')}")
    y -= 30

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Type Distribution:")
    y -= 20
    p.setFont("Helvetica", 11)
    for eq_type, count in dist.items():
        p.drawString(70, y, f"- {eq_type}: {count}")
        y -= 18
        if y < 80:  # new page if we run out of space
            p.showPage()
            y = height - 50
            p.setFont("Helvetica", 11)

    p.showPage()
    p.save()
    buf.seek(0)

    filename = "latest_equipment_report.pdf"
    return FileResponse(buf, as_attachment=True, filename=filename)


@api_view(['POST'])
def login_view(request):
    """
    Body: { "username": "...", "password": "..." }
    Returns: { "token": "...", "username": "..." }
    """
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"detail": "Username and password required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = authenticate(request, username=username, password=password)
    if not user:
        return Response(
            {"detail": "Invalid credentials."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    token, created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key, "username": user.username})


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Requires Authorization: Token <token>
    Deletes the token on the server.
    """
    if request.auth:
        request.auth.delete()  # delete the Token object
    return Response({"detail": "Logged out."})


@api_view(['GET'])
def dataset_latest_rows(request):
    """
    Returns the first 50 rows of the latest dataset (raw CSV rows).
    Uses the Dataset.raw_data JSON field.
    """
    ds = Dataset.objects.order_by('-uploaded_at').first()
    if not ds:
        return Response(
            {"detail": "No datasets yet."},
            status=status.HTTP_404_NOT_FOUND,
        )

    rows = getattr(ds, "raw_data", []) or []

    return Response({
        "filename": ds.name,
        "rows": rows[:50],  # first 50 rows only
        "total_rows": len(rows),
    })
