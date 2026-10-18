"""
report_export.py
Exports historical sensor + carbon savings data as CSV, and generates a
short PDF summary suitable for statutory/administrative reporting.
"""

import csv
import io
from datetime import date, datetime

from fpdf import FPDF

from .models import SensorReading, CarbonSaving
from .database import SessionLocal


# ---------------------------------------------------------------------------
# CSV export
# ---------------------------------------------------------------------------
def export_csv(start_date: date, end_date: date, output_path: str = None) -> str:
    """
    Exports sensor_readings and carbon_savings for [start_date, end_date]
    (inclusive) as CSV text. If output_path is given, also writes the file
    to disk. Returns the CSV content as a string either way.
    """
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")

    session = SessionLocal()
    try:
        start_dt = datetime(start_date.year, start_date.month, start_date.day)
        end_dt = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)

        sensor_rows = (
            session.query(SensorReading)
            .filter(
                SensorReading.timestamp >= start_dt, SensorReading.timestamp <= end_dt
            )
            .order_by(SensorReading.timestamp)
            .all()
        )
        carbon_rows = (
            session.query(CarbonSaving)
            .filter(CarbonSaving.date >= start_date, CarbonSaving.date <= end_date)
            .order_by(CarbonSaving.date)
            .all()
        )

        buffer = io.StringIO()
        writer = csv.writer(buffer)

        writer.writerow(["-- Sensor Readings --"])
        writer.writerow(["timestamp", "source_type", "value", "unit"])
        for r in sensor_rows:
            writer.writerow([r.timestamp.isoformat(), r.source_type, r.value, r.unit])

        writer.writerow([])
        writer.writerow(["-- Carbon Savings (daily) --"])
        writer.writerow(
            [
                "date",
                "kwh_from_renewable",
                "kwh_from_grid",
                "co2_saved_kg",
                "grid_dependence_pct",
            ]
        )
        for c in carbon_rows:
            writer.writerow(
                [
                    c.date.isoformat(),
                    c.kwh_from_renewable,
                    c.kwh_from_grid,
                    c.co2_saved_kg,
                    c.grid_dependence_pct,
                ]
            )

        csv_content = buffer.getvalue()

        if output_path:
            with open(output_path, "w", newline="") as f:
                f.write(csv_content)

        return csv_content
    finally:
        session.close()


# ---------------------------------------------------------------------------
# PDF summary export
# ---------------------------------------------------------------------------
class SummaryPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(
            0, 10, "Hybrid Renewable Energy Optimization System", ln=True, align="C"
        )
        self.set_font("Helvetica", "", 11)
        self.cell(
            0, 8, "Carbon Savings & Grid Dependence Summary Report", ln=True, align="C"
        )
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def export_pdf_summary(
    start_date: date, end_date: date, output_path: str = "carbon_summary.pdf"
) -> str:
    """
    Generates a short PDF summarizing total CO2 saved, average grid
    dependence reduction, and a per-day table, for [start_date, end_date].
    Returns the output_path the file was written to.
    """
    if start_date > end_date:
        raise ValueError("start_date must not be after end_date")

    session = SessionLocal()
    try:
        carbon_rows = (
            session.query(CarbonSaving)
            .filter(CarbonSaving.date >= start_date, CarbonSaving.date <= end_date)
            .order_by(CarbonSaving.date)
            .all()
        )

        total_co2_saved = round(sum(r.co2_saved_kg for r in carbon_rows), 2)
        total_renewable = round(sum(r.kwh_from_renewable for r in carbon_rows), 2)
        total_grid = round(sum(r.kwh_from_grid for r in carbon_rows), 2)
        avg_grid_dependence = (
            round(sum(r.grid_dependence_pct for r in carbon_rows) / len(carbon_rows), 2)
            if carbon_rows
            else 0.0
        )

        pdf = SummaryPDF()
        pdf.add_page()

        pdf.set_font("Helvetica", "", 11)
        pdf.cell(
            0,
            8,
            f"Report period: {start_date.isoformat()} to {end_date.isoformat()}",
            ln=True,
        )
        pdf.cell(
            0,
            8,
            f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            ln=True,
        )
        pdf.ln(4)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Key Metrics", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"Total CO2 saved: {total_co2_saved} kg", ln=True)
        pdf.cell(0, 7, f"Total renewable energy used: {total_renewable} kWh", ln=True)
        pdf.cell(0, 7, f"Total grid energy used: {total_grid} kWh", ln=True)
        pdf.cell(0, 7, f"Average grid dependence: {avg_grid_dependence}%", ln=True)
        pdf.ln(6)

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Daily Breakdown", ln=True)
        pdf.set_font("Helvetica", "B", 10)

        col_widths = [30, 35, 30, 30, 40]
        headers = [
            "Date",
            "Renewable (kWh)",
            "Grid (kWh)",
            "CO2 saved (kg)",
            "Grid dependence (%)",
        ]
        for w, h in zip(col_widths, headers):
            pdf.cell(w, 8, h, border=1, align="C")
        pdf.ln()

        pdf.set_font("Helvetica", "", 10)
        for row in carbon_rows:
            pdf.cell(col_widths[0], 8, row.date.isoformat(), border=1, align="C")
            pdf.cell(col_widths[1], 8, str(row.kwh_from_renewable), border=1, align="C")
            pdf.cell(col_widths[2], 8, str(row.kwh_from_grid), border=1, align="C")
            pdf.cell(col_widths[3], 8, str(row.co2_saved_kg), border=1, align="C")
            pdf.cell(
                col_widths[4], 8, str(row.grid_dependence_pct), border=1, align="C"
            )
            pdf.ln()

        pdf.ln(6)
        pdf.set_font("Helvetica", "I", 9)
        pdf.multi_cell(
            0,
            6,
            "Note: CO2 savings use the grid average emission factor "
            "(0.727 kg CO2/kWh, CEA CO2 Baseline Database v20.0, FY 2023-24). "
            "Update this factor when CEA publishes a newer version.",
        )

        pdf.output(output_path)
        return output_path
    finally:
        session.close()

if __name__ == "__main__":
    from sqlalchemy import func as _func

    session = SessionLocal()
    try:
        earliest = session.query(_func.min(CarbonSaving.date)).scalar()
        latest = session.query(_func.max(CarbonSaving.date)).scalar()
    finally:
        session.close()

    if not earliest or not latest:
        print("No rows in carbon_savings yet — run carbon_analytics.py first.")
    else:
        csv_text = export_csv(earliest, latest, output_path="sample_export.csv")
        print(
            f"CSV export written to sample_export.csv (range: {earliest} to {latest})"
        )
        print(csv_text[:300], "...")

        pdf_path = export_pdf_summary(
            earliest, latest, output_path="sample_summary.pdf"
        )
        print(f"PDF summary written to {pdf_path}")
