from components.libs.basic import *
from sentence_transformers import util
from jose import JWTError, jwt
from openai import AsyncOpenAI
import re
from konlpy.tag import Okt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import time


okt = Okt()
API_KEY = ""
client = AsyncOpenAI(api_key=API_KEY)


def mmr(doc_embedding, candidate_embeddings, words, top_n, diversity):

    # 문서와 각 키워드들 간의 유사도가 적혀있는 리스트
    word_doc_similarity = cosine_similarity(candidate_embeddings, doc_embedding)

    # 각 키워드들 간의 유사도
    word_similarity = cosine_similarity(candidate_embeddings)

    # 문서와 가장 높은 유사도를 가진 키워드의 인덱스를 추출.
    # 만약, 2번 문서가 가장 유사도가 높았다면
    # keywords_idx = [2]
    keywords_idx = [np.argmax(word_doc_similarity)]

    # 가장 높은 유사도를 가진 키워드의 인덱스를 제외한 문서의 인덱스들
    # 만약, 2번 문서가 가장 유사도가 높았다면
    # ==> candidates_idx = [0, 1, 3, 4, 5, 6, 7, 8, 9, 10 ... 중략 ...]
    candidates_idx = [i for i in range(len(words)) if i != keywords_idx[0]]

    # 최고의 키워드는 이미 추출했으므로 top_n-1번만큼 아래를 반복.
    # ex) top_n = 5라면, 아래의 loop는 4번 반복됨.
    for _ in range(top_n - 1):
        try:
            candidate_similarities = word_doc_similarity[candidates_idx, :]
            target_similarities = np.max(word_similarity[candidates_idx][:, keywords_idx], axis=1)

            # MMR을 계산
            mmr = (1-diversity) * candidate_similarities - diversity * target_similarities.reshape(-1, 1)
            mmr_idx = candidates_idx[np.argmax(mmr)]

            # keywords & candidates를 업데이트
            keywords_idx.append(mmr_idx)
            candidates_idx.remove(mmr_idx)
        except:
            pass
        
    result = [words[idx] for idx in keywords_idx]
    return result


async def create_room(similarity_model, roomId, roomMaxCnt, gameOverTimer, roomTheme, question):
    data = pd.DataFrame()
    today =  datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "status":200,
        "message":"success"
    }


    embedding_basic = similarity_model.encode([roomTheme + "??????????"])
    embedding_question = similarity_model.encode([question])
    cosine_scores = util.cos_sim(embedding_basic, embedding_question)
    score = [float(item.numpy()) for item in cosine_scores]
    score = score[0] * float(np.sqrt(np.sum(np.power(embedding_basic[0], 2.0)))) / float(np.sqrt(np.sum(np.power(embedding_question[0], 2.0))))

    if score < 0.45:
        result = {
            "status":404,
            "message":"not enough question",
            "object": round(score, 2),
        }
        return result

    SECRET_KEY = "20240118TOSSBOMB"
    ALGORITHM = "HS256"
    payload = {
        'id': roomId,
        'pw' : roomTheme,
        'exp': datetime.datetime.utcnow()
    }
    hashedRoomId = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    data['user_id'] = [roomId]
    data['room_id'] = [hashedRoomId]
    data['room_theme'] = [roomTheme]
    data['room_max_cnt'] = [roomMaxCnt]
    data['room_curr_cnt'] = [0]
    data['game_over_time'] = [gameOverTimer]
    data['room_alive_check'] = [1]
    data['created_at'] = [today]

    result['hashedRoomId'] = hashedRoomId

    try:
        insert_df_to_db(True, "bombtoss_room_info", data)
    except:
        result = {
            "status":500,
            "message":"DB Insert Error",
        }
    result["object"] = score
    return result

async def room_user_info(hashedRoomId):
    result = {
        "status":200,
        "message":"success"
    }
    df = load_db_query(True, f'select * from bombtoss_user_info where room_id="{hashedRoomId}"')
    data = []
    if len(df) > 0:
        for nickname, status, position, host_check in zip(df['nickname'].values, df['status'].values, df['position'].values, df['host_check'].values):
            data.append({"nickname":str(nickname), "status":str(status), "position":int(position), "host_check":int(host_check)})
    result['object'] = data

    return result

async def register_user(hashedRoomId, nickname, hostCheck):
    data = pd.DataFrame()
    today =  datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
    result = {
        "status":200,
        "message":"success"
    }

    data['room_id'] = [hashedRoomId]
    data['nickname'] = [nickname]
    data['status'] = ["준비 완료"]
    data['position'] = [-1]
    data['host_check'] = [int(hostCheck)]
    data['updated_at'] = [today]

    try:
        insert_df_to_db(True, "bombtoss_user_info", data)
    except:
        result = {
            "status":500,
            "message":"DB Insert Error"
        }
    
    return result


async def game_start(roomId, hostCheck):
    result = {
        "status":200,
        "message":"success"
    }
    if hostCheck:
        today =  datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
        df = load_db_query(True, f'select * from bombtoss_user_info where room_id="{roomId}"')
        pre_data = []
        if len(df) > 0:
            for nickname, status, position, host_check in zip(df['nickname'].values, df['status'].values, df['position'].values, df['host_check'].values):
                pre_data.append({"userNickname":str(nickname), "userStatus":str(status), "position":int(position), "hostCheck":int(host_check)})

        data = pd.DataFrame()
        position_ = [i for i in range(len(pre_data))]
        np.random.shuffle(position_)
        data['room_id'] = [roomId for _ in range(len(pre_data))]
        data['nickname'] = [row["userNickname"] for row in pre_data]
        data['status'] = ["게임중" for _ in range(len(pre_data))]
        data['position'] = list(position_)
        data['host_check'] = [row["hostCheck"] for row in pre_data]
        data['updated_at'] = [today for _ in range(len(pre_data))]

        condList = [{
            "room_id":f'"{roomId}"'
        }]
        try:
            delete_bulk_db(True, "bombtoss_user_info", condList)
        except:
            result = {
                "status":500,
                "message":"DB Delete Error"
            }
        try:
            insert_df_to_db(True, "bombtoss_user_info", data)
        except:
            result = {
                "status":500,
                "message":"DB Update Error"
            }
        
    else:
        result = {
            "status":400,
            "message":"You are not host!"
        }

    return result

async def game_user_update(roomId, nickname, status, position):
    result = {
        "status":200,
        "message":"success"
    }
    today =  datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
    df = load_db_query(True, f'select * from bombtoss_user_info where room_id="{roomId}" and nickname="{nickname}"')
    pre_data = []
    if len(df) > 0:
        for nickname_, status_, position_, host_check_ in zip(df['nickname'].values, df['status'].values, df['position'].values, df['host_check'].values):
            pre_data.append({"userNickname":str(nickname_), "userStatus":str(status_), "position":int(position_), "hostCheck":int(host_check_)})

    data = pd.DataFrame()
    data['room_id'] = [roomId for _ in range(len(pre_data))]
    data['nickname'] = [row["userNickname"] for row in pre_data]
    data['status'] = [status for _ in range(len(pre_data))]
    data['position'] = [position for _ in range(len(pre_data))]
    data['host_check'] = [row["hostCheck"] for row in pre_data]
    data['updated_at'] = [today for _ in range(len(pre_data))]

    condList = [{
        "room_id":f'"{roomId}"',
        "nickname":f'"{nickname}"'
    }]
    try:
        delete_bulk_db(True, "bombtoss_user_info", condList)
    except:
        result = {
            "status":500,
            "message":"DB Delete Error"
        }
    try:
        insert_df_to_db(True, "bombtoss_user_info", data)
    except:
        result = {
            "status":500,
            "message":"DB Update Error"
        }
    
    return result

async def create_game_data_info(roomId, initQuestion, currTimer):
    result = {
        "status":200,
        "message":"success"
    }
    today =  datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")
    start_position = 0
    df = load_db_query(True, f'select * from bombtoss_user_info where room_id="{roomId}" and position={start_position}')
    df_room = load_db_query(True, f'select * from bombtoss_room_info where room_id="{roomId}"')

    if len(df)>0 and len(df_room)>0:
        start_nickname = str(df['nickname'].values[0])
        roomTheme = str(df_room['room_theme'].values[-1])
        data = pd.DataFrame()
        data['room_id'] = [roomId]
        data['room_theme'] = [roomTheme]
        data['curr_nickname'] = [start_nickname]
        data['curr_position'] = [start_position]
        data['curr_question'] = [initQuestion]
        data['curr_answer'] = [""]
        data['curr_round'] = [1]
        data['curr_timer'] = [currTimer]
        data['updated_at'] = [today]

        print(data)

        try:
            insert_df_to_db(True, "bombtoss_game_info", data)
        except:
            result = {
                "status":500,
                "message":"DB Update Error"
            }
    else:
        result = {
            "status":404,
            "message":"cannot found user or room"
        }
    
    return result

async def get_game_data_info(roomId):
    df = load_db_query(True, f'select * from bombtoss_game_info where room_id="{roomId}"')
    result = {
        "status":200,
        "message":"success"
    }
    if len(df)>0:
        data = []
        for curr_nickname_, curr_position_, curr_question_, curr_answer_, curr_round_, curr_timer_, room_theme_ in zip(df['curr_nickname'].values, df['curr_position'].values, df['curr_question'].values, df['curr_answer'].values, df['curr_round'].values, df['curr_timer'].values, df['room_theme'].values):
            data.append({
                "curr_nickname":str(curr_nickname_),
                "curr_position":int(curr_position_),
                "curr_question":str(curr_question_),
                "curr_answer":str(curr_answer_),
                "curr_round":int(curr_round_),
                "curr_timer":int(curr_timer_),
                "room_theme": str(room_theme_),
            })
        result['object'] = data[-1]
    else:
        result = {
            "status":400,
            "message":"room not found"
        }
    
    return result

async def update_game_data_info(roomId, currNickname, currPosition, currQuestion, currAnswer, currRound, currTimer):
    result = {
        "status":200,
        "message":"success"
    }
    df = load_db_query(True, f'select * from bombtoss_game_info where room_id="{roomId}"')
    df_room = load_db_query(True, f'select * from bombtoss_room_info where room_id="{roomId}"')

    if len(df)>0 and len(df_room)>0:
        if currTimer == -100:
            currTimer = int(df['curr_timer'].values[-1])
        elif currTimer == -200:
            currTimer = int(df_room['game_over_time'].values[-1])

        condList = [{
            "room_id":f'"{roomId}"'
        }]
        try:
            delete_bulk_db(True, "bombtoss_game_info", condList)
        except:
            result = {
                "status":500,
                "message":"DB Delete Error"
            }
        today =  datetime.datetime.now(timezone('Asia/Seoul')).strftime("%Y-%m-%d %H:%M:%S")

        data = pd.DataFrame()
        data['room_id'] = [roomId]
        data['curr_nickname'] = [currNickname]
        data['curr_position'] = [currPosition]
        data['curr_question'] = [currQuestion]
        data['curr_answer'] = [currAnswer]
        data['curr_round'] = [currRound]
        data['curr_timer'] = [currTimer]
        data['room_theme'] = [str(df_room['room_theme'].values[-1])]
        data['updated_at'] = [today]

        try:
            insert_df_to_db(True, "bombtoss_game_info", data)
        except:
            result = {
                "status":500,
                "message":"DB Update Error"
            }

    return result


async def answer_check(similarity_model, roomId, question, answer):
    result = {
        "status":200,
        "message":"success"
    }

    df = load_db_query(True, f'select * from bombtoss_room_info where room_id="{roomId}"')
    if len(df)>0:
        roomTheme = df['room_theme'].values[-1]
        embedding_basic = similarity_model.encode([roomTheme, question])
        embedding_answer = similarity_model.encode([answer])
        cosine_scores = util.cos_sim(embedding_basic, embedding_answer)
        result["object"] = [float(item.numpy()) for item in cosine_scores]
        result["object"][0] = result["object"][0] * float(np.sqrt(np.sum(np.power(embedding_basic[0], 2.0)))) / float(np.sqrt(np.sum(np.power(embedding_answer[0], 2.0)))) + 0.1
        result["object"][1] = result["object"][1] * float(np.sqrt(np.sum(np.power(embedding_basic[1], 2.0)))) / float(np.sqrt(np.sum(np.power(embedding_answer[0], 2.0)))) + 0.1
    else:
        result = {
            "status":404,
            "message":"room not found"
        }
    return result


async def question_check(similarity_model, roomId, pastQuestion, question):
    result = {
        "status":200,
        "message":"success"
    }

    df = load_db_query(True, f'select * from bombtoss_room_info where room_id="{roomId}"')
    if len(df)>0:
        roomTheme = df['room_theme'].values[-1]
        embedding_basic = similarity_model.encode([roomTheme + "??????????", pastQuestion])
        embedding_question = similarity_model.encode([question])
        cosine_scores = util.cos_sim(embedding_basic, embedding_question)
        result["object"] = [float(item.numpy()) for item in cosine_scores]
        result["object"][0] = result["object"][0] * float(np.sqrt(np.sum(np.power(embedding_basic[0], 2.0)))) / float(np.sqrt(np.sum(np.power(embedding_question[0], 2.0))))
        result["object"][1] = result["object"][1] * float(np.sqrt(np.sum(np.power(embedding_basic[1], 2.0)))) / float(np.sqrt(np.sum(np.power(embedding_question[0], 2.0))))
    else:
        result = {
            "status":404,
            "message":"room not found"
        }
    return result


async def generate_question(similarity_model, targetNickname, roomId, pastQuestion, pastAnswer, question_prompt):
    result = {
        "status":200,
        "message":"success"
    }

    data = pd.DataFrame()
    data['room_id'] = [roomId]
    data['question'] = [pastQuestion]
    data['answer'] = [pastAnswer]

    try:
        insert_df_to_db(True, "bombtoss_qa_info", data)
    except:
        result = {
            "status":500,
            "message":"DB Update Error"
        }

    df = load_db_query(True, f'select * from bombtoss_room_info where room_id="{roomId}"')
    try:
        df_qa = load_db_query(True, f'select * from bombtoss_qa_info where room_id="{roomId}"')
    except:
        df_qa = pd.DataFrame()
        df_qa['question'] = []
        df_qa['answer'] = []
        pass

    if len(df)>0:
        roomTheme = str(df['room_theme'].values[-1]).strip()
        doc = ""
        for q, a in zip(df_qa['question'].values, df_qa['answer'].values):
            doc += f"{pastQuestion}\n{pastAnswer}\n"
        doc_embedding = similarity_model.encode([roomTheme])

        okt_pos = okt.pos(doc)
        word_list = []
        for word in okt_pos:
            if word[1] not in ['Josa', 'Eomi', 'Punctuation', 'Verb', 'Adjective', 'Suffix', 'Adverb']:
                if len(word[0]) > 1:
                    word_list.append(word[0])

        doc=' '.join(word_list)
        count = CountVectorizer(ngram_range=(1,1), stop_words="english").fit([doc])
        keywords_from_doc = count.get_feature_names_out()
        keyword_embedding = similarity_model.encode(keywords_from_doc)
        keywords = mmr(doc_embedding, keyword_embedding, keywords_from_doc, top_n=100, diversity=0.0)

        props = {}
        props[f"신규 질문"] = {
            "type":"string",
            "description":f"신규 질문의 주제 및 키워드와 최근 키워드에 어울리는 무작위 질문을 ?로 마무리 지어서 생성하기"
        }
        props[f"적합도"] = {
            "type":"integer",
            "description":f"생성한 신규 질문이 신규 질문의 주제 및 키워드와 최근 키워드에 얼마나 어울리는지 1~100 사이의 숫자로 표시하기"
        }
        function_call = [{
            "name": "additional_question",
            "description": f"{targetNickname} 을 꼭 언급하여 신규 질문을 의문문으로 생성하기",
            "parameters": {
                "title":"신규 질문",
                "type":"object",
                "properties": props,
                "required": list(props.keys())
            }
        }]

        query0 = f'''
        신규 질문의 내용은 "{question_prompt}"에 대해서 의문형으로 생성해야 합니다.
        '''

        query1 = f'''
        신규 질문을 받을 대상은 {targetNickname} 입니다.
        신규 질문의 주제는 다음과 같습니다.
        '''

        query2 = f'''
        다음에 올 내용은 최근 키워드입니다.
        '''

        past_keywords= f'''"{'", "'.join(keywords)}"'''

        query4 = f'''
        신규 질문은 흥미진진하고 최대한 간결해야 합니다. 결과물은 json 형태로 리턴되어야 합니다. 
        '''

        messages = []
        messages.append({"role":"system", "content":query0})
        #messages.append({"role":"system", "content":persona1})
        messages.append({"role":"system", "content":query1})
        messages.append({"role":"system", "content":roomTheme})
        messages.append({"role":"system", "content":query2})
        messages.append({"role":"system", "content":past_keywords})
        #messages.append({"role":"system", "content":query3})
        #messages.append({"role":"system", "content":stop_questions})
        messages.append({"role":"system", "content":query4})

        result_fin = {}
        bug_cnt = 0
        while True:
            if bug_cnt > 3:
                break
            completion = await client.with_options(timeout=20, max_retries=5).chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=messages,
                temperature=1.0,
                frequency_penalty=0.0,
                functions=function_call,
                function_call="auto",
                response_format={"type": "json_object"},
            )
            result_text = completion.choices[0].message 
            print(result_text)
            try:
                result_ = result_text.function_call.arguments
                result_ = re.sub('[\n]', '', result_)
                result_fin = json.loads(result_)
            except:
                result_fin = {}
                print("Not Yet....", result_text)
                time.sleep(3)
                bug_cnt += 1
                continue

            if "신규 질문" in result_fin:
                break

        result['object'] = result_fin

    else:
        result = {
            "status":404,
            "message":"room not found"
        }
    return result