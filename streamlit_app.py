import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import json

# Cargar credenciales desde el archivo de secretos
key_dict = json.loads(st.secrets["textkey"])
creds = service_account.Credentials.from_service_account_info(key_dict)
db = firestore.Client(credentials=creds, project="names-project-demo-1f588")

dbNames = db.collection("names")

st.header("Nuevo registro")

# Inputs para ingresar datos
index = st.text_input("Index")
name = st.text_input("Name")
sex = st.selectbox("Select Sex", ('F', 'M', 'Other'))

submit = st.button("Crear nuevo registro")

# Guardar datos en Firestore
if index and name and sex and submit:
    doc_ref = db.collection("names").document(name)
    doc_ref.set({
        "index": index,
        "name": name,
        "sex": sex
    })
    st.sidebar.write("Registro insertado correctamente")

# Función para buscar por nombre
def loadByName(name):
    names_ref = dbNames.where('name', '==', name).stream()
    currentName = None
    for myname in names_ref:
        currentName = myname
    return currentName

st.sidebar.subheader("Buscar nombre")
nameSearch = st.sidebar.text_input("nombre")
btnFiltrar = st.sidebar.button("Buscar")

if btnFiltrar:
    doc = loadByName(nameSearch)
    if doc is None:
        st.sidebar.write("Nombre no existe")
    else:
        st.sidebar.write(doc.to_dict())

st.sidebar.markdown("---")
btnEliminar = st.sidebar.button("Eliminar")

if btnEliminar:
    deletename = loadByName(nameSearch)
    if deletename is None:
        st.sidebar.write(f"{nameSearch} no existe")
    else:
        dbNames.document(deletename.id).delete()
        st.sidebar.write(f"{nameSearch} eliminado")

st.sidebar.markdown("---")
newname = st.sidebar.text_input("Actualizar nombre")
btnActualizar = st.sidebar.button("Actualizar")

if btnActualizar:
    updatename = loadByName(nameSearch)
    if updatename is None:
        st.write(f"{nameSearch} no existe")
    else:
        myupdatename = dbNames.document(updatename.id)
        myupdatename.update({"name": newname})

# Mostrar la base de datos en un DataFrame
names_ref = list(db.collection(u"names").stream())
names_dict = list(map(lambda x: x.to_dict(), names_ref))
names_dataframe = pd.DataFrame(names_dict)
st.dataframe(names_dataframe)
