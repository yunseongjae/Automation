import streamlit as st
import pandas as pd
import datetime
import requests
import json
import csv

class preprocess:
    def window():
        st.session_state.날짜 = datetime.today()
        st.session_state.키 = '2p766ucn1hesgnn7py2701uhmjl8rvhm'
        st.session_state.아이디 = 'numble'
        st.session_state.발신자 = '01099712034'
        st.session_state.발신주소 = 'https://apis.aligo.in/send/'

    def processing(file):
        file['전화번호'] = file['전화번호'].astype('str').apply(lambda x: '0' + x)
        file['destination'] = file['전화번호'] + "|" + file['이름']

        des_list = file['destination'].tolist()
        st.session_state.목적지리스트= ','.join(des_list)

        rec_list = file['전화번호'].tolist()
        st.session_state.번호리스트= ','.join(rec_list)


        msg_dict ={
                'key': '2p766ucn1hesgnn7py2701uhmjl8rvhm', #api key
                'userid': 'numble', # 알리고 사이트 아이디
                'sender': '01099712034', # 발신번호
                'receiver': st.session_state.번호리스트, # 수신번호 (,활용하여 1000명까지 추가 가능)
                'msg': '%고객명% test', #문자 내용
                'msg_type' : 'SMS', #메세지 타입 (SMS, LMS)
                'title' : 'title', #메세지 제목 (장문에 적용)
                'destination' : st.session_state.목적지리스트, # %고객명% 치환용 입력
                'rdate' : '예약날짜',
                'rtime' : '예약시간'}

        return file, msg_dict

    def msg_processing(message):
        message['dday'] = message['일자'].apply(lambda x: x.split('+')[1])
        return message

    def msg_generate(message_list, msg_dict):
        today = datetime.datetime.today()
        msg_list = []
        for i in range(message_list.shape[0]):
            msg_dict['msg'] = message_list['내용'][i]
            msg_dict['rdate'] = str((today + datetime.timedelta(days=int(message_list['dday'][i]))).strftime('%Y-%m-%d')).replace("-",'')
            msg_dict['rtime'] = "1900"
            msg_df = pd.DataFrame.from_dict([msg_dict])
            msg_list.append(msg_df)
        return msg_list

    def send_msg(msg_dict):
        send_url = 'https://apis.aligo.in/send/'

        sms_data=msg_dict

        send_response = requests.post(send_url, data=sms_data[0])

        return send_response.json()['success_cnt']
st.header("상시챌린지 자동 문자발송 시스템")



col1, col2 = st.columns(2)
with col1:
    reg_list = st.file_uploader("참가자 명단 파일을 업로드해주세요")


with col2:
    msg_list = st.file_uploader("주차별 메세지 파일을 업로드해주세요")


if reg_list is not None:
    df_total = pd.read_excel(reg_list)
    df_total_result, msg_dict_result = preprocess.processing(df_total)


if msg_list is not None:
    message = pd.read_excel(msg_list)
    message_result = preprocess.msg_processing(message)
    message_result = preprocess.msg_generate(message_result,msg_dict_result)
    for i in message_result:
        st.dataframe(i)

    if st.button("메세지 전송하기"):
        for i in message_result:
            i_dict = i.to_dict('records')
            response = preprocess.send_msg(i_dict) 
            if response == "1":
                st.write("전송 완료되었습니다.")
            else:
                st.write("전송 실패하였습니다. ")
