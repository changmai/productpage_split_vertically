import os
import streamlit as st
from PIL import Image
import tempfile
import shutil
import zipfile

st.set_page_config(page_title="이미지 분할기", layout="centered")
st.title("📷 이미지 수직 분할기")
st.markdown("이미지를 선택하고, 원하는 타일 높이를 입력하세요. 이미지의 가로 길이는 자동으로 원본 기준으로 처리됩니다.")

uploaded_file = st.file_uploader("이미지 파일 업로드 (JPG, PNG)", type=["jpg", "jpeg", "png"])
tile_height = st.number_input("타일 높이 (px)", min_value=3000, max_value=10000, value=3000, step=100)

if uploaded_file is not None:
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            img = Image.open(file_path)
            img_width, img_height = img.size
            basename = os.path.splitext(os.path.basename(file_path))[0]
            output_dir = os.path.join(temp_dir, f"{basename}_slices")
            os.makedirs(output_dir, exist_ok=True)

            count = 0
            for top in range(0, img_height, tile_height):
                box = (0, top, img_width, min(top + tile_height, img_height))
                tile = img.crop(box)
                tile_filename = f"{basename}_part_{count}.jpg"
                tile.save(os.path.join(output_dir, tile_filename))
                count += 1

            # 압축파일 생성
            zip_path = os.path.join(temp_dir, f"{basename}_slices.zip")
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for filename in os.listdir(output_dir):
                    file_full_path = os.path.join(output_dir, filename)
                    zipf.write(file_full_path, arcname=filename)

            st.success(f"{count}개의 이미지로 분할 완료되었습니다.")
            with open(zip_path, "rb") as f:
                st.download_button(
                    label="📦 분할 이미지 ZIP 다운로드",
                    data=f,
                    file_name=f"{basename}_slices.zip",
                    mime="application/zip"
                )
        except Exception as e:
            st.error(f"이미지 처리 중 오류 발생: {e}")
