import streamlit as st
from agent import BRANDS,create
from pathlib import Path
st.set_page_config(page_title="Brand Post Studio",layout="wide")
st.title("Brand Post Studio | 4 Brands")
st.caption("Offline template mode works without API key. AI copy mode requires OPENAI_API_KEY.")
brand=st.selectbox("Marka",list(BRANDS),format_func=lambda x:BRANDS[x]['name'])
mode=st.selectbox("Üretim modu",["offline","ai"],format_func=lambda x:"Şablon / Demo" if x=="offline" else "AI metin üretimi (API)")
idx=st.selectbox("Kütüphane örneği",range(3),format_func=lambda i:BRANDS[brand]['topics'][i][0])
topic=st.text_input("AI modu için özel konu (isteğe bağlı)")
if st.button("Post oluştur",type="primary"):
 try:
  path,meta=create(brand,idx,topic or None,mode,Path(__file__).parent/'preview.png')
  st.image(str(path),width=450);st.json(meta)
  st.download_button("PNG indir",path.read_bytes(),file_name=f"{brand}_post.png",mime="image/png")
 except Exception as e:st.error(str(e))
