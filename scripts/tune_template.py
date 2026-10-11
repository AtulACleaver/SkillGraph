#!/usr/bin/env python3
"""Tune docs/report/template.docx to produce a compact layout (tight margins, smaller spacing)."""

import io
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = ROOT / "docs" / "report" / "template.docx"


def main():
    if not TEMPLATE_PATH.exists():
        print(f"Error: {TEMPLATE_PATH} does not exist")
        return

    buf = io.BytesIO(TEMPLATE_PATH.read_bytes())
    new_buf = io.BytesIO()

    with zipfile.ZipFile(buf, "r") as zin, zipfile.ZipFile(
        new_buf, "w", zipfile.ZIP_DEFLATED
    ) as zout:
        for item in zin.infolist():
            content = zin.read(item.filename)
            if item.filename == "word/document.xml":
                text = content.decode("utf-8")
                # Insert 0.4-inch top/bottom and 0.45-inch left/right margins into sectPr
                pg_mar = '<w:pgMar w:top="576" w:right="648" w:bottom="576" w:left="648" w:header="280" w:footer="280" w:gutter="0"/>'
                text = re.sub(
                    r"<w:sectPr>",
                    f"<w:sectPr>{pg_mar}",
                    text,
                )
                content = text.encode("utf-8")
            elif item.filename == "word/styles.xml":
                text = content.decode("utf-8")
                # Make Normal paragraph spacing compact (after=30 dxa = 1.5pt, line=200)
                text = re.sub(
                    r'<w:spacing w:after="200"\s*/>',
                    '<w:spacing w:after="30" w:line="200" w:lineRule="auto" />',
                    text,
                )
                text = re.sub(
                    r'<w:spacing w:after="80" w:line="240" w:lineRule="auto"\s*/>',
                    '<w:spacing w:after="20" w:line="200" w:lineRule="auto" />',
                    text,
                )
                text = re.sub(
                    r'<w:spacing w:before="180" w:after="180"\s*/>',
                    '<w:spacing w:before="60" w:after="30" />',
                    text,
                )
                # Reduce body font size to 9pt (val=18)
                text = re.sub(r'<w:sz w:val="24"\s*/>', '<w:sz w:val="18" />', text)
                text = re.sub(
                    r'<w:szCs w:val="24"\s*/>', '<w:szCs w:val="18" />', text
                )
                content = text.encode("utf-8")
            zout.writestr(item, content)

    TEMPLATE_PATH.write_bytes(new_buf.getvalue())
    print("Successfully tuned docs/report/template.docx for compact layout.")


if __name__ == "__main__":
    main()
