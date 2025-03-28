import streamlit as st
from openai import OpenAI
import json

st.set_page_config(layout="wide")


if "participantes" not in st.session_state:
    st.session_state.participantes = "Sem participantes"

if "resumo" not in st.session_state:
    st.session_state.resumo = "Sem resumo"

if "texto" not in st.session_state:
    st.session_state.texto = "Sem texto"

if "escolhido" not in st.session_state:
    st.session_state.escolhido = ["Sem participantes"]

client = OpenAI()

def ask_openai(system, prompt):
    
    if system == "":
        return "Como posso ajudá-lo?"
    try:
        print("Iniciando chat")
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (f"{system}")
                },
                {
                    "role": "user",
                    "content": (f"{prompt}")
                }
            ],

            temperature=1,
            max_tokens=10000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0

            )
        
        answer = completion.choices[0].message.content
        answer = answer.replace("`","").replace("json","") 
        print(f"answer: {answer}")
        return answer
    
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
        return None

    except Exception as e:
        print(f"Erro inesperado: {e}")
        return None

col1, col2 = st.columns(2)

with col1:
    with st.form("gerador_texto"):
        st.session_state.texto = st.text_area("Insira o texto aqui para extrair os participantes")
        enviar_texto = st.form_submit_button("Enviar texto")
        
        if enviar_texto:
            system =  '''Você é um computador que extrai os dados de um texto e responde somente  como uma lista:
                        participantes = [Karin giselle, Paulo Senna, cinthia cardoso, renato olandesi]
                    '''
            prompt = f'''
                        Responda somente como um texto em formato de lista todos os participantes dessa conversa utilizando o seguinte exemplo:
                        ["Alex viana", "Karin Giselle", "Eduardo borges", "Railton lima"]
                        Extraia os dados do seguinte texto: {st.session_state.texto}
                    '''
            st.session_state.participantes = ask_openai(system, prompt)
            if st.session_state.participantes != "Sem participantes":
                st.session_state.participantes = st.session_state.participantes.replace('"','')
                st.session_state.participantes = st.session_state.participantes.replace('[','')
                st.session_state.participantes = st.session_state.participantes.replace(']','')
                st.session_state.participantes = st.session_state.participantes.strip()
                st.session_state.participantes = st.session_state.participantes.split(',')

with col2:
    with st.form("resumos"):
        
        st.session_state.escolhido = st.pills("Selecione um participante",st.session_state.participantes, selection_mode="multi")
        #st.session_state.escolhido = escolhido    
        #st.write(f"Voce selecionou: {st.session_state.escolhido}")
        #if escolhido != "Sem participantes":
        #    escolhido = ["Sem participantes"]
        #    if escolhido[0] == st.session_state.participantes:
                #st.write(st.session_state.escolhido)
                #st.write(st.session_state.participantes)
        #        st.warning("Primeiro extraia participantes de uma conversa")
        
        extrair = st.form_submit_button("Extrair resumo")
        if extrair:
            system = '''
                        Você é um computador que extrai os dados de um texto de um determinado participante fazendo resumos a cada 5 minutos
                        Exemplo:
                        { "0-5": "Fulano falou sobre imprevistos",
                        "5-10":"Fulano citou que está com problemas e precisa de ajuda",
                        "45-50": "Fulano disse que terminaria uma task ainda hoje"
                        }
                    '''
            prompt = f'''
                        Extraia de maneira detalhada o conteúdo do texto somente para o(s) participante(s) selecionados resumindo o conteudo a cada 5 minutos conforme e responda somente em formato markdown, nunca extraia dados referentes a particpantes que não estejam selecionados:
                    
                        texto = {st.session_state.texto}
                        participantes = {st.session_state.escolhido}
                    
                    '''+''' Exemplo:
                                #0-5: 
                                - Fulano falou sobre imprevistos
                                - Cicrano disse falou sobre outro assunto detalhadamente
                                #5-10
                                - Fulano citou que está com problemas e precisa de ajuda
                                #45-50
                                - Fulano disse que terminaria uma task ainda hoje
                                - Beltano agradeceu pela ajuda
                            
                    '''
            st.session_state.resumo = ask_openai(system, prompt)

with st.container(key="chat"):
    st.markdown(st.session_state.resumo)