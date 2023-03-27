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
def convert_qr(
    input_str: str,
    output_format: str,
    scale: int,
    border: int,
    dark_color: str,
    light_color: str,
):
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
        qrcode.save(
            image,
            kind="png",
            border=border,
            scale=scale,
            dark=dark_color,
            light=light_color,
        )
        return image

    elif output_format == "SVG":
        return qrcode.svg_inline(
            border=border, scale=scale, dark=dark_color, light=light_color
        )


def handle_convert_qr():
    input_str: str = st.session_state.input
    output_format: str = st.session_state.format
    scale: int = st.session_state.get("scale", 2)
    border: int = st.session_state.get("border", 4)
    dark_color: str = st.session_state.get("dark_color", "#000000")
    light_color: str = st.session_state.get("light_color", "#ffffff")

    with output_container:
        if not input_str:
            st.info("Please write some text to encode into QR")
            return

        output_data = convert_qr(
            input_str, output_format, scale, border, dark_color, light_color
        )
        if output_format == "Text":
            st.code(output_data, language=None)

        elif output_format == "PNG":
            st.image(output_data)
            st.download_button(
                "Download PNG", output_data, "qr.png", key="download_png"
            )

        elif output_format == "SVG":
            st.image(output_data)
            st.code(output_data, language="svg")
            st.download_button(
                "Download SVG", output_data, "qr.svg", key="download_svg"
            )


with form_container:
    st.text_area(
        "Input text",
        key="input",
        value="https://example.com",
        on_change=handle_convert_qr,
        max_chars=500,
    )

    input_format = st.radio(
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

    if input_format != "Text":
        st.slider(
            "Scale",
            min_value=1,
            max_value=100,
            value=4,
            key="scale",
            on_change=handle_convert_qr,
        )

        st.slider(
            "Border",
            min_value=0,
            max_value=10,
            value=4,
            key="border",
            on_change=handle_convert_qr,
        )

        col1, col2 = st.columns(2)
        col1.color_picker(
            "Dark color", value="#000000", key="dark_color", on_change=handle_convert_qr
        )
        col2.color_picker(
            "Light color",
            value="#ffffff",
            key="light_color",
            on_change=handle_convert_qr,
        )

    st.button(
        "Render", on_click=handle_convert_qr, use_container_width=True, key="render"
    )
