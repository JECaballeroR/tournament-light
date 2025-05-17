import streamlit as st
import time
import uuid
import requests
from datetime import timedelta
from streamlit_autorefresh import st_autorefresh

# ==================== CONFIGURACIÓN ====================
import os

API_KEY = os.getenv("GOVEE_API_KEY")
DEVICE = os.getenv("GOVEE_DEVICE")
MODEL = os.getenv("GOVEE_MODEL")

HEADERS = {
    "Content-Type": "application/json",
    "Govee-API-Key": API_KEY
}

URL = "https://openapi.api.govee.com/router/api/v1/device/control"

# ======================================================


def activate_dynamic_scene(paramid=18137, scene_id=10825):
    body = {
        "requestId": str(uuid.uuid4()),
        "payload": {
            "sku": MODEL,
            "device": DEVICE,
            "capability": {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "lightScene",
                "value": {
                    "paramId": paramid,
                    "id": scene_id
                }
            }
        }
    }
    requests.post(URL, headers=HEADERS, json=body)


def activate_diy_scene(scene_value=15868780):
    body = {
        "requestId": str(uuid.uuid4()),
        "payload": {
            "sku": MODEL,
            "device": DEVICE,
            "capability": {
                "type": "devices.capabilities.dynamic_scene",
                "instance": "diyScene",
                "value": scene_value
            }
        }
    }
    requests.post(URL, headers=HEADERS, json=body)


# ==================== STREAMLIT ====================
st.set_page_config(page_title="Temporizador de Torneo", layout="centered")
st.title("🕒 Temporizador de Torneo con Govee")

# Estado compartido
if "torneo_activo" not in st.session_state:
    st.session_state.torneo_activo = False
    st.session_state.start_time = None
    st.session_state.duracion = 0
    st.session_state.notified_orange = False
    st.session_state.notified_red = False

# Formulario para iniciar torneo
if not st.session_state.torneo_activo:
    with st.form("inicio_torneo"):
        minutos = st.number_input("Duración del torneo (minutos):", min_value=1, step=1)
        submitted = st.form_submit_button("Iniciar torneo")
        if submitted:
            st.session_state.duracion = minutos
            st.session_state.start_time = time.time()
            st.session_state.torneo_activo = True
            st.session_state.notified_orange = False
            st.session_state.notified_red = False
            activate_dynamic_scene()
            st.success("Torneo iniciado")
            st.rerun()

# Si el torneo está activo
if st.session_state.torneo_activo:
    st_autorefresh(interval=1000, key="contador")  # Refresca cada 1s

    tiempo_total = st.session_state.duracion * 60
    elapsed = time.time() - st.session_state.start_time
    remaining = int(tiempo_total - elapsed)

    if remaining < 0:
        st.success("✅ Torneo terminado.")
        activate_diy_scene(13378902)  # Azul final
        st.session_state.torneo_activo = False
    else:
        mins, secs = divmod(remaining, 60)
        st.markdown(f"## ⏳ Tiempo restante: `{mins:02d}:{secs:02d}`")

        # Notificación mitad de tiempo
        if not st.session_state.notified_orange and elapsed == tiempo_total / 2:
            activate_diy_scene(15868780)  # Naranja
            time.sleep(5)
            activate_dynamic_scene()
            st.session_state.notified_orange = True
            st.toast("🟠 Mitad del tiempo")

        # Notificación último minuto
        red_trigger = 50 if st.session_state.duracion == 1 else tiempo_total - 60
        if not st.session_state.notified_red and elapsed >= red_trigger:
            activate_diy_scene(15894307)  # Rojo
            time.sleep(5)
            activate_dynamic_scene()
            st.session_state.notified_red = True
            st.toast("🔴 Último minuto")
