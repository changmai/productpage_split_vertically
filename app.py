import os
import streamlit as st
from PIL import Image
import tempfile
import zipfile

st.set_page_config(page_title="이미지 분할기", layout="centered")
st.title("📷 이미지 수직 분할기")
st.markdown(
    "이미지를 선택하고, 원하는 타일 높이를 입력하세요. 이미지의 가로 길이는 자동으로 원본 기준으로 처리됩니다.")

# 업로드 허용 파일 확장자
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

uploaded_file = st.file_uploader(
    "이미지 파일 업로드 (JPG, PNG)", type=[ext.strip('.') for ext in ALLOWED_EXTENSIONS]
)
tile_height = st.number_input(
    "타일 높이 (px)", min_value=3000, max_value=15000, value=3000, step=500
)

if uploaded_file is not None:
    # 임시 디렉토리 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        try:
            img = Image.open(file_path)
            img_width, img_height = img.size

            # 예상 분할 개수
            estimated_count = (img_height + tile_height - 1) // tile_height
            st.info(f"총 {estimated_count}개의 이미지로 분할됩니다.")

            if st.button("📸 사진 분할 시작"):
                basename, ext = os.path.splitext(os.path.basename(file_path))
                ext = ext.lower()
                # 출력 포맷 결정
                if ext in ['.jpg', '.jpeg']:
                    out_format = 'JPEG'
                    out_ext = '.jpg'
                else:
                    out_format = 'PNG'
                    out_ext = '.png'

                output_dir = os.path.join(temp_dir, f"{basename}_slices")
                os.makedirs(output_dir, exist_ok=True)

                count = 0
                for top in range(0, img_height, tile_height):
                    box = (0, top, img_width, min(top + tile_height, img_height))
                    tile = img.crop(box)
                    # 투명도 있는 이미지는 RGB로 변환
                    if out_format == 'JPEG' and tile.mode in ('RGBA', 'P'):
                        tile = tile.convert('RGB')

                    tile_filename = f"{basename}_part_{count}{out_ext}"
                    save_params = {}
                    if out_format == 'JPEG':
                        save_params = {'quality': 100, 'subsampling': 0}

                    tile.save(
                        os.path.join(output_dir, tile_filename),
                        format=out_format,
                        **save_params
                    )
                    count += 1

                # ZIP 생성
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
