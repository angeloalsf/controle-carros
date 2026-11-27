import re
from datetime import date
import streamlit as st
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from config import get_mongodb_uri

st.set_page_config(page_title="Sistema de Controle de Carros", page_icon="🚗", layout="wide")

@st.cache_resource
def get_database():
    uri = get_mongodb_uri()
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    return client["controle_carros"]

try:
    db = get_database()
    carros = db["carros"]
    proprietarios = db["proprietarios"]
    manutencoes = db["manutencoes"]

    # Índices para garantir unicidade e melhorar consultas.
    carros.create_index("placa", unique=True)
    proprietarios.create_index("cpf", unique=True)
except Exception as exc:
    st.error("Não foi possível conectar ao MongoDB.")
    st.info("Verifique sua conexão com a internet e a linha MONGODB_URI do arquivo .env.")
    st.code(str(exc))
    st.stop()

def oid(value):
    return ObjectId(value) if value else None

def money(value):
    return f"R$ {float(value):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def owner_options():
    return list(proprietarios.find().sort("nome", 1))

def car_options():
    return list(carros.find().sort("placa", 1))

def owner_label(owner):
    return f'{owner["nome"]} — CPF {owner["cpf"]}'

def car_label(car):
    return f'{car["placa"]} — {car["marca"]} {car["modelo"]} ({car["ano"]})'

st.title("Sistema de Controle de Carros")
st.caption("Cadastro e gerenciamento de veículos, proprietários e manutenções.")

# Indicadores
c1, c2, c3 = st.columns(3)
c1.metric("Veículos cadastrados", carros.count_documents({}))
c2.metric("Proprietários cadastrados", proprietarios.count_documents({}))
c3.metric("Manutenções registradas", manutencoes.count_documents({}))

tab_carros, tab_prop, tab_manut, tab_buscas = st.tabs(
    ["Carros", "Proprietários", "Manutenções", "Consultas"]
)

with tab_carros:
    st.subheader("Gerenciamento de carros")
    ac, ec, lc = st.tabs(["Cadastrar", "Editar / Excluir", "Listar"])
    with ac:
        owners = owner_options()
        if not owners:
            st.warning("Cadastre pelo menos um proprietário antes de cadastrar um carro.")
        else:
            with st.form("form_carro_novo", clear_on_submit=True):
                col1, col2, col3 = st.columns(3)
                marca = col1.text_input("Marca*")
                modelo = col2.text_input("Modelo*")
                ano = col3.number_input("Ano*", min_value=1900, max_value=2100, value=2022, step=1)
                col4, col5, col6 = st.columns(3)
                cor = col4.text_input("Cor")
                placa = col5.text_input("Placa*").strip().upper()
                km = col6.number_input("Quilometragem (km)", min_value=0, value=0, step=100)
                combustivel = st.selectbox("Combustível", ["Flex", "Gasolina", "Etanol", "Diesel", "Elétrico", "Híbrido", "GNV"])
                dono = st.selectbox("Proprietário*", owners, format_func=owner_label)
                submitted = st.form_submit_button("Cadastrar carro")
                if submitted:
                    if not marca.strip() or not modelo.strip() or not placa or not dono:
                        st.error("Preencha os campos obrigatórios.")
                    else:
                        try:
                            carros.insert_one({
                                "marca": marca.strip(), "modelo": modelo.strip(), "ano": int(ano),
                                "cor": cor.strip(), "placa": placa, "quilometragem": int(km),
                                "combustivel": combustivel, "proprietario_id": dono["_id"]
                            })
                            st.success("Carro cadastrado com sucesso.")
                            st.rerun()
                        except DuplicateKeyError:
                            st.error("Já existe um veículo cadastrado com essa placa.")
                        except PyMongoError as e:
                            st.error(f"Erro ao cadastrar: {e}")
    with ec:
        lista = car_options()
        if not lista:
            st.info("Nenhum carro cadastrado.")
        else:
            selected = st.selectbox("Selecione o veículo", lista, format_func=car_label, key="car_edit_select")
            current = carros.find_one({"_id": selected["_id"]})
            owners = owner_options()
            owner_ids = [str(o["_id"]) for o in owners]
            current_owner = str(current.get("proprietario_id", ""))
            owner_index = owner_ids.index(current_owner) if current_owner in owner_ids else 0
            with st.form("form_carro_editar"):
                a, b, c = st.columns(3)
                marca = a.text_input("Marca", current.get("marca", ""))
                modelo = b.text_input("Modelo", current.get("modelo", ""))
                ano = c.number_input("Ano", min_value=1900, max_value=2100, value=int(current.get("ano", 2022)))
                d, e, f = st.columns(3)
                cor = d.text_input("Cor", current.get("cor", ""))
                placa = e.text_input("Placa", current.get("placa", "")).strip().upper()
                km = f.number_input("Quilometragem (km)", min_value=0, value=int(current.get("quilometragem", 0)))
                combustiveis = ["Flex", "Gasolina", "Etanol", "Diesel", "Elétrico", "Híbrido", "GNV"]
                combustivel = st.selectbox("Combustível", combustiveis,
                    index=combustiveis.index(current.get("combustivel")) if current.get("combustivel") in combustiveis else 0)
                dono = st.selectbox("Proprietário", owners, index=owner_index, format_func=owner_label) if owners else None
                salvar = st.form_submit_button("Salvar alterações")
                if salvar:
                    if not marca.strip() or not modelo.strip() or not placa or not dono:
                        st.error("Preencha os campos obrigatórios.")
                    else:
                        try:
                            carros.update_one({"_id": current["_id"]}, {"$set": {
                                "marca": marca.strip(), "modelo": modelo.strip(), "ano": int(ano),
                                "cor": cor.strip(), "placa": placa, "quilometragem": int(km),
                                "combustivel": combustivel, "proprietario_id": dono["_id"]
                            }})
                            st.success("Veículo atualizado.")
                            st.rerun()
                        except DuplicateKeyError:
                            st.error("Já existe outro veículo com essa placa.")
            if st.button("Excluir veículo selecionado", type="secondary", key="delete_car"):
                if manutencoes.count_documents({"carro_id": current["_id"]}) > 0:
                    st.error("Não é possível excluir: existem manutenções vinculadas. Exclua primeiro essas manutenções.")
                else:
                    carros.delete_one({"_id": current["_id"]})
                    st.success("Veículo excluído.")
                    st.rerun()
    with lc:
        docs = list(carros.find().sort("placa", 1))
        if docs:
            rows = []
            for car in docs:
                owner = proprietarios.find_one({"_id": car.get("proprietario_id")})
                rows.append({
                    "Placa": car.get("placa"), "Marca": car.get("marca"), "Modelo": car.get("modelo"),
                    "Ano": car.get("ano"), "Cor": car.get("cor"), "Quilometragem": car.get("quilometragem"),
                    "Combustível": car.get("combustivel"), "Proprietário": owner.get("nome") if owner else "Não encontrado"
                })
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum veículo cadastrado.")

with tab_prop:
    st.subheader("Gerenciamento de proprietários")
    ap, ep, lp = st.tabs(["Cadastrar", "Editar / Excluir", "Listar"])
    with ap:
        with st.form("form_owner_new", clear_on_submit=True):
            nome = st.text_input("Nome*")
            cpf = st.text_input("CPF*")
            telefone = st.text_input("Telefone")
            email = st.text_input("E-mail")
            submit = st.form_submit_button("Cadastrar proprietário")
            if submit:
                if not nome.strip() or not cpf.strip():
                    st.error("Nome e CPF são obrigatórios.")
                else:
                    try:
                        proprietarios.insert_one({"nome": nome.strip(), "cpf": cpf.strip(),
                            "telefone": telefone.strip(), "email": email.strip()})
                        st.success("Proprietário cadastrado.")
                        st.rerun()
                    except DuplicateKeyError:
                        st.error("Já existe um proprietário com esse CPF.")
    with ep:
        owners = owner_options()
        if not owners:
            st.info("Nenhum proprietário cadastrado.")
        else:
            selected = st.selectbox("Selecione o proprietário", owners, format_func=owner_label, key="owner_edit_select")
            with st.form("form_owner_edit"):
                nome = st.text_input("Nome", selected.get("nome", ""))
                cpf = st.text_input("CPF", selected.get("cpf", ""))
                telefone = st.text_input("Telefone", selected.get("telefone", ""))
                email = st.text_input("E-mail", selected.get("email", ""))
                save = st.form_submit_button("Salvar alterações")
                if save:
                    if not nome.strip() or not cpf.strip():
                        st.error("Nome e CPF são obrigatórios.")
                    else:
                        try:
                            proprietarios.update_one({"_id": selected["_id"]}, {"$set": {
                                "nome": nome.strip(), "cpf": cpf.strip(),
                                "telefone": telefone.strip(), "email": email.strip()
                            }})
                            st.success("Proprietário atualizado.")
                            st.rerun()
                        except DuplicateKeyError:
                            st.error("Já existe outro proprietário com esse CPF.")
            if st.button("Excluir proprietário selecionado", key="delete_owner"):
                if carros.count_documents({"proprietario_id": selected["_id"]}) > 0:
                    st.error("Não é possível excluir: existem veículos vinculados a este proprietário.")
                else:
                    proprietarios.delete_one({"_id": selected["_id"]})
                    st.success("Proprietário excluído.")
                    st.rerun()
    with lp:
        docs = list(proprietarios.find().sort("nome", 1))
        if docs:
            st.dataframe([{"Nome": x.get("nome"), "CPF": x.get("cpf"),
                "Telefone": x.get("telefone"), "E-mail": x.get("email")} for x in docs],
                use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum proprietário cadastrado.")

with tab_manut:
    st.subheader("Gerenciamento de manutenções")
    am, em, lm = st.tabs(["Cadastrar", "Editar / Excluir", "Listar"])
    with am:
        cars = car_options()
        if not cars:
            st.warning("Cadastre um veículo antes de registrar uma manutenção.")
        else:
            with st.form("form_maintenance_new", clear_on_submit=True):
                car = st.selectbox("Veículo*", cars, format_func=car_label)
                tipo = st.selectbox("Tipo*", ["Troca de óleo", "Revisão", "Pneus", "Freios", "Motor", "Elétrica", "Outro"])
                descricao = st.text_area("Descrição")
                data_m = st.date_input("Data", value=date.today())
                km_m = st.number_input("Quilometragem na manutenção", min_value=0, value=int(car.get("quilometragem", 0)))
                valor = st.number_input("Valor (R$)", min_value=0.0, value=0.0, step=10.0)
                submit = st.form_submit_button("Registrar manutenção")
                if submit:
                    manutencoes.insert_one({"carro_id": car["_id"], "tipo": tipo, "descricao": descricao.strip(),
                        "data": data_m.isoformat(), "quilometragem": int(km_m), "valor": float(valor)})
                    st.success("Manutenção registrada.")
                    st.rerun()
    with em:
        ms = list(manutencoes.find().sort("data", -1))
        if not ms:
            st.info("Nenhuma manutenção cadastrada.")
        else:
            def mlabel(m):
                car = carros.find_one({"_id": m.get("carro_id")})
                return f'{m.get("data")} — {car.get("placa") if car else "Veículo removido"} — {m.get("tipo")}'
            selected = st.selectbox("Selecione a manutenção", ms, format_func=mlabel, key="maintenance_edit_select")
            with st.form("form_maintenance_edit"):
                cars = car_options()
                if cars:
                    car_ids = [str(c["_id"]) for c in cars]
                    idx = car_ids.index(str(selected["carro_id"])) if str(selected["carro_id"]) in car_ids else 0
                    car = st.selectbox("Veículo", cars, index=idx, format_func=car_label)
                tipo_opts = ["Troca de óleo", "Revisão", "Pneus", "Freios", "Motor", "Elétrica", "Outro"]
                tipo = st.selectbox("Tipo", tipo_opts, index=tipo_opts.index(selected.get("tipo")) if selected.get("tipo") in tipo_opts else 0)
                descricao = st.text_area("Descrição", selected.get("descricao", ""))
                try:
                    current_date = date.fromisoformat(selected.get("data", date.today().isoformat()))
                except ValueError:
                    current_date = date.today()
                data_m = st.date_input("Data", value=current_date)
                km_m = st.number_input("Quilometragem", min_value=0, value=int(selected.get("quilometragem", 0)))
                valor = st.number_input("Valor (R$)", min_value=0.0, value=float(selected.get("valor", 0)))
                save = st.form_submit_button("Salvar alterações")
                if save:
                    if cars:
                        manutencoes.update_one({"_id": selected["_id"]}, {"$set": {
                            "carro_id": car["_id"], "tipo": tipo, "descricao": descricao.strip(),
                            "data": data_m.isoformat(), "quilometragem": int(km_m), "valor": float(valor)
                        }})
                        st.success("Manutenção atualizada.")
                        st.rerun()
            if st.button("Excluir manutenção selecionada", key="delete_maintenance"):
                manutencoes.delete_one({"_id": selected["_id"]})
                st.success("Manutenção excluída.")
                st.rerun()
    with lm:
        ms = list(manutencoes.find().sort("data", -1))
        if ms:
            rows = []
            for m in ms:
                car = carros.find_one({"_id": m.get("carro_id")})
                rows.append({"Data": m.get("data"), "Placa": car.get("placa") if car else "—",
                    "Tipo": m.get("tipo"), "Descrição": m.get("descricao"),
                    "Quilometragem": m.get("quilometragem"), "Valor": money(m.get("valor", 0))})
            st.dataframe(rows, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhuma manutenção cadastrada.")

with tab_buscas:
    st.subheader("Consultas ao banco de dados")
    search_type = st.selectbox("Escolha uma consulta", [
        "1. Buscar veículo pela placa",
        "2. Buscar veículos por marca",
        "3. Buscar veículos por ano",
        "4. Buscar veículos por proprietário",
        "5. Histórico de manutenção de um veículo",
        "6. Total gasto com manutenção por veículo"
    ])
    if search_type.startswith("1."):
        placa = st.text_input("Digite a placa").strip().upper()
        if st.button("Pesquisar", key="search_plate") and placa:
            result = carros.find_one({"placa": placa})
            if result:
                owner = proprietarios.find_one({"_id": result.get("proprietario_id")})
                st.write({"Marca": result.get("marca"), "Modelo": result.get("modelo"),
                    "Ano": result.get("ano"), "Placa": result.get("placa"),
                    "Proprietário": owner.get("nome") if owner else "Não encontrado"})
            else:
                st.warning("Nenhum veículo encontrado.")
    elif search_type.startswith("2."):
        marcas = sorted([x for x in carros.distinct("marca") if x])
        marca = st.selectbox("Marca", marcas) if marcas else None
        if st.button("Pesquisar", key="search_brand") and marca:
            st.dataframe(list(carros.find({"marca": {"$regex": f"^{re.escape(marca)}$", "$options": "i"}},
                {"_id": 0, "marca": 1, "modelo": 1, "ano": 1, "placa": 1})), use_container_width=True)
    elif search_type.startswith("3."):
        ano = st.number_input("Mostrar veículos fabricados a partir de:", min_value=1900, max_value=2100, value=2020)
        if st.button("Pesquisar", key="search_year"):
            results = list(carros.find({"ano": {"$gte": int(ano)}}, {"_id": 0, "marca": 1, "modelo": 1, "ano": 1, "placa": 1}).sort("ano", 1))
            if results:
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.info("Nenhum veículo encontrado.")
    elif search_type.startswith("4."):
        owners = owner_options()
        owner = st.selectbox("Proprietário", owners, format_func=owner_label) if owners else None
        if st.button("Pesquisar", key="search_owner") and owner:
            results = list(carros.find({"proprietario_id": owner["_id"]}, {"_id": 0, "marca": 1, "modelo": 1, "ano": 1, "placa": 1}))
            if results:
                st.dataframe(results, use_container_width=True, hide_index=True)
            else:
                st.info("Esse proprietário não possui veículos cadastrados.")
    elif search_type.startswith("5."):
        cars = car_options()
        car = st.selectbox("Veículo", cars, format_func=car_label) if cars else None
        if st.button("Pesquisar", key="search_history") and car:
            results = list(manutencoes.find({"carro_id": car["_id"]}, {"_id": 0}).sort("data", -1))
            if results:
                st.dataframe([{"Data": x.get("data"), "Tipo": x.get("tipo"), "Descrição": x.get("descricao"),
                    "Quilometragem": x.get("quilometragem"), "Valor": money(x.get("valor", 0))} for x in results],
                    use_container_width=True)
            else:
                st.info("Não há manutenções registradas para esse veículo.")
    else:
        pipeline = [
            {"$group": {"_id": "$carro_id", "total_gasto": {"$sum": "$valor"}, "quantidade": {"$sum": 1}}},
            {"$lookup": {"from": "carros", "localField": "_id", "foreignField": "_id", "as": "carro"}},
            {"$unwind": {"path": "$carro", "preserveNullAndEmptyArrays": True}},
            {"$project": {"_id": 0, "placa": "$carro.placa", "marca": "$carro.marca",
                "modelo": "$carro.modelo", "quantidade_manutencoes": "$quantidade", "total_gasto": 1}},
            {"$sort": {"total_gasto": -1}}
        ]
        if st.button("Executar agregação", key="search_cost"):
            results = list(manutencoes.aggregate(pipeline))
            if results:
                st.dataframe([{"Placa": x.get("placa", "—"), "Veículo": f'{x.get("marca", "")} {x.get("modelo", "")}'.strip() or "Veículo removido",
                    "Manutenções": x.get("quantidade_manutencoes"), "Total gasto": money(x.get("total_gasto", 0))}
                    for x in results], use_container_width=True, hide_index=True)
            else:
                st.info("Ainda não existem manutenções registradas.")

st.divider()
st.caption("Trabalho acadêmico — Tópicos Especiais em Banco de Dados | MongoDB")
