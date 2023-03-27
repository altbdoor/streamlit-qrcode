import streamlit as st
import segno
import io


st.set_page_config(
    menu_items={
        "About": "https://github.com/altbdoor/streamlit-qrcode",
    }
)
st.title(
    """
    QRCode generated with [segno](https://pypi.org/project/segno/)
    """
)

# st.write("""
# <style>
# </style>
# """, unsafe_allow_html=True)

form_container = st.container()
output_container = st.container()
output_container.markdown("---")


@st.cache_data
def convert_qr(input_str: str, output_format: str, scale: int):
    qrcode = segno.make_qr(input_str)

    if output_format == "Text":
        qr_lines: list[str] = []

        with io.StringIO() as qr_text:
            qrcode.save(qr_text, kind="txt", border=0)
            qr_lines = qr_text.getvalue().strip().split("\n")

        qr_linecount = len(qr_lines)

        if qr_linecount % 2 != 0:
            qr_lines.append("0" * len(qr_lines[0]))
            qr_linecount += 1

        qr_linecount = qr_linecount // 2
        qr_map = [(idx * 2, idx * 2 + 1) for idx in range(0, qr_linecount)]

        qr_remapped: str = ""
        for row_current_idx, row_next_idx in qr_map:
            for col_idx, col_current in enumerate(qr_lines[row_current_idx]):
                col_next = qr_lines[row_next_idx][col_idx]

                if col_current == "1" and col_next == "1":
                    qr_remapped += "█"
                elif col_current == "1" and col_next == "0":
                    qr_remapped += "▀"
                elif col_current == "0" and col_next == "1":
                    qr_remapped += "▄"
                else:
                    qr_remapped += " "

            qr_remapped += "\n"

        return qr_remapped

    elif output_format == "PNG":
        image = io.BytesIO()
        qrcode.save(image, kind="png", border=0, scale=scale)
        return image

    elif output_format == "SVG":
        return qrcode.svg_inline(border=0, scale=scale, light="#fff")


def handle_convert_qr():
    input_str: str = st.session_state.input
    output_format: str = st.session_state.format
    scale: int = st.session_state.scale

    with output_container:
        if not input_str:
            st.info("Please write some text to encode into QR")
            return

        output_data = convert_qr(input_str, output_format, scale)
        if output_format == "Text":
            st.code(output_data, language=None)

        elif output_format == "PNG":
            st.image(output_data)
            st.download_button("Download PNG", output_data, "qr.png")

        elif output_format == "SVG":
            st.image(output_data)
            st.code(output_data, language="svg")
            st.download_button("Download SVG", output_data, "qr.svg")


with form_container:
    st.text_area(
        "Input text",
        key="input",
        value="https://example.com",
        on_change=handle_convert_qr,
        max_chars=500,
    )
    st.slider(
        "Scale (does not work with text output)",
        min_value=1,
        max_value=100,
        value=4,
        key="scale",
        on_change=handle_convert_qr,
    )
    st.radio(
        "Render output",
        options=(
            "PNG",
            "SVG",
            "Text",
        ),
        key="format",
        index=0,
        on_change=handle_convert_qr,
    )
    st.button("Render", on_click=handle_convert_qr, use_container_width=True)
