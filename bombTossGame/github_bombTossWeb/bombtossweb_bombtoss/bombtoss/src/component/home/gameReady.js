import { useState, useEffect } from "react";
import { useNavigate, useParams } from 'react-router-dom';
import styled from "styled-components";
import bombImg from "../../assets/img/bomb.png";
import axios from "axios";
import { useWs } from "../hook/webSocket";

export const GameReady =()=> {
	const navigate = useNavigate();
    const params = useParams();
	const roomIdOrigin = `${params.room_id}`;
    const roomMaxCnt = parseInt(`${params.room_max_cnt}`);
    const [hostCheck, setHostCheck] = useState(false);
    const [user, setUser] = useState([
    ]);
    const [nickname, setNickname] = useState(null);
    const [registerStatus, setRegisterStatus] = useState(true);
    const [roomStatus, setRoomStatus] = useState("대기중");
    const [timer, setTimer] = useState(false);
    const [loadFirstData, setLoadFirstData] = useState(false);
    const [gameStartStatus, setGameStartStatus] = useState(false);
    const [registeredNickname, setRegisteredNickname] = useState(false);
    const [gameStartClick, setGameStartClick] = useState(false);
    const [registerClick, setRegisterClick] = useState(false);

    const [userReady, userSend] = useWs(`ws://bitbox.iptime.org:9091/ws/gameReady`, setUser);

    useEffect(() => {
        if(!gameStartStatus){
            if(userReady) {
                userSend(JSON.stringify({roomId: roomIdOrigin}));
            }
        }
    }, [userReady, roomIdOrigin]);

    useEffect(()=>{
        loadDataEvent();
    }, []);

    useEffect(()=>{
        fetchData(user, nickname);
    }, [user]);

    useEffect(() => {
        const nickname_ = null;
        const hostCheck_ = window.sessionStorage.getItem('firstQuestion');
        if(!hostCheck_||hostCheck_==="null") {
            setHostCheck(false);
            window.sessionStorage.setItem('nickname', null);
        } else {
            setHostCheck(true);
        }
        setNickname(nickname_);
        //fetchData(nickname_);
	  }, [roomIdOrigin]);


    useEffect(() => {
        if(user?.length>=roomMaxCnt){
            setRegisterClick(true);
        }
    }, [user?.length]);
    
    useEffect(()=>{
        if(roomStatus!=="준비 완료" && roomStatus!=="대기중" && roomStatus<=5 && roomStatus>0){
            var startTimer = setTimeout(()=>{ setRoomStatus(roomStatus - 1) }, 1000);
        } else if(roomStatus===0){
            navigate(`/progress/${roomIdOrigin}/${roomMaxCnt}/ongoing`);
        } else {
            loadDataEvent();
        }
    },[roomStatus]);

    const loadDataEvent = async()=> {
        try {
            const response = await axios.get(`/gameReadyResult/${roomIdOrigin}`);
        } catch {
            alert("서버 오류!");
        }
    }

    const fetchData = async (userVal, nickname_)=> {
        const nicknameCheck = userVal?.filter((row)=>row.nickname===nickname_);
        const userStatus = userVal?.filter((row)=>row.status==="게임중");
        setLoadFirstData(true);
        if(nicknameCheck?.length > 0 && nickname_){
            setRegisterStatus(true);
        } else {
            setRegisterStatus(false);
        }

        if(userStatus?.length>0){
            if(hostCheck){
                try {
                    const token_data = {
                        username:"sejinlim",
                        password:"Jammanbo2@"
                    };
                    const token_response = await axios.post(`/token`,
                        token_data,
                        {
                            headers: {
                                "Content-Type": "application/x-www-form-urlencoded",
                            }
                        }
                    );
                    try {
                        const data2 = {
                            hostNickname: nickname,
                            initQuestion: window.sessionStorage.getItem('firstQuestion'),
                            currTimer: window.sessionStorage.getItem('gameOverTimer'),
                        }
                        const response2 = await axios.post(`/createGameDataInfo/${roomIdOrigin}`,
                            data2,
                            {
                                headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
                            }
                        );
                    } catch {
                        alert("서버 오류!");
                    }
                } catch {
                    alert("서버 오류!");
                }
            }
            setRoomStatus(5);
        } else if(roomMaxCnt===userVal?.length && userStatus?.length===0){
            setRoomStatus("준비 완료");
        }
    }

    const setNicknameEvent =(e)=> {
		setNickname(e.target.value);
	}

	const handleOnKeyPress = (e) => {
		if (e.key === 'Enter') {
			registerNickname();
		}
	};

    const registerNickname = async ()=> {
        setRegisterClick(true);
        var nicknameCheck = user.filter((row)=>row.nickname===nickname);
        if(nickname && nicknameCheck?.length === 0 && user.length < roomMaxCnt){
            window.sessionStorage.setItem('nickname', nickname);
            
            try {
                const token_data = {
                    username:"sejinlim",
                    password:"Jammanbo2@"
                };
                const token_response = await axios.post(`/token`,
                    token_data,
                    {
                        headers: {
                            "Content-Type": "application/x-www-form-urlencoded",
                        }
                    }
                );
                try {
                    const data = {
                        nickname: nickname,
                    }
                    const response = await axios.post(`/registerUser/${roomIdOrigin}/${hostCheck}`,
                        data,
                        {
                            headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
                        }
                    );
                    loadDataEvent();
                    setRegisteredNickname(true);
                } catch {
                    alert("서버 오류!");
                    setRegisterClick(false);
                }
            } catch {
                alert("서버 오류!");
                setRegisterClick(false);
            }
        } else if(nicknameCheck?.length === 0 && user.length >= roomMaxCnt){
            alert("최대 수용 인원이 꽉 찼습니다!");
            setRegisterClick(false);
        } else if(nicknameCheck?.length > 0 && user.length < roomMaxCnt){
            alert("이미 등록된 닉네임 입니다.");
            setRegisterClick(false);
        } else{
            alert("닉네임을 입력해주세요.");
            setRegisterClick(false);
        }
    }
    
    const hostStartGame =async()=> {
        setGameStartClick(true);
        setGameStartStatus(false);
        try {
            const token_data = {
                username:"sejinlim",
                password:"Jammanbo2@"
            };
            const token_response = await axios.post(`/token`,
                token_data,
                {
                    headers: {
                        "Content-Type": "application/x-www-form-urlencoded",
                    }
                }
            );
            try {
                const response = await axios.get(`/gameStart/${roomIdOrigin}/${hostCheck}`,
                    {
                        headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
                    }
                );
                setGameStartStatus(true);
                loadDataEvent();
            } catch {
                alert("서버 오류!");
                setGameStartStatus(false);
            }
        } catch {
            alert("서버 오류!");
            setGameStartStatus(false);
        }
    }

	return(
		<Container>
			<VerticalDiv height={"20%"}>
				<ContentDiv>
					<LabelField width={"20rem"}>
						질문 폭탄 게임
					</LabelField>
				</ContentDiv>
				<ContentDiv>
					<LabelField fontSize={"1.5rem"} width={"20rem"}>
						대기실
					</LabelField>
				</ContentDiv>
			</VerticalDiv>
			<VerticalDiv height={"30rem"}>
				<ContentDiv>
					<LabelField fontSize={"1.2rem"} width={"10rem"}>
						최대 수용 인원
					</LabelField>
                    <LabelField fontSize={"1.2rem"} width={"10rem"}>
						{roomMaxCnt}
					</LabelField>
                </ContentDiv>
                <ContentDiv>
					<LabelField fontSize={"1.2rem"} width={"10rem"}>
						현재 대기 인원
					</LabelField>
                    <LabelField fontSize={"1.2rem"} width={"10rem"}>
						{user.length}
					</LabelField>
                </ContentDiv>
                <LabelField fontSize={"1rem"} width={"10rem"}>
					대기 명단
                </LabelField>
                <VerticalDiv2 height={"100%"}>
                    <ScrollDiv maxHeight={"90%"}>
                        {user.map((row, rowIdx)=>{
                            return(
                                <ContentDiv>
                                    <LabelField fontSize={"1.2rem"} width={"10rem"}>
                                        {rowIdx+1}
                                    </LabelField>
                                    <LabelField fontSize={"1.2rem"} width={"10rem"}>
                                        {row.nickname}
                                    </LabelField>
                                    <LabelField fontSize={"1.2rem"} width={"10rem"}>
                                        {row.status}
                                    </LabelField>
                                </ContentDiv>
                            );
                        })}
                    </ScrollDiv>
                </VerticalDiv2>
                {registerStatus?(
                    <ContentDiv>
                    </ContentDiv>
                ):!nickname&&parseInt(roomStatus)>0?(
                    <ContentDiv>
                        <LabelField fontSize={"1.2rem"} width={"20rem"}>
                            게임 관전을 시작합니다
                        </LabelField>
                    </ContentDiv>
                ):!registerClick?(
                    <ContentDiv>
                        <LabelField fontSize={"1.2rem"} width={"10rem"}>
                            닉네임 입력
                        </LabelField>
                        {!registeredNickname?<TextField type="text" onChange={setNicknameEvent} onKeyPress={handleOnKeyPress}></TextField>:<LabelField></LabelField>}
                    </ContentDiv>
                ):null}
			</VerticalDiv>
			<VerticalDiv height={"40%"}>
                {!registerStatus&&user?.length<roomMaxCnt&&loadFirstData&&!registeredNickname&&!registerClick?(
                    <BombDiv>
                        <ContentDiv>
                            <LabelField fontSize={"1rem"} display={"none"}>
                                대기 명단 등록!
                            </LabelField>
                        </ContentDiv>
                        <ContentDiv>
                            <BombImg src={bombImg} onClick={()=>registerNickname()} />
                        </ContentDiv>
                    </BombDiv>
                ):hostCheck&&roomStatus==="대기중"?(
                    <BombDiv>
                        <ContentDiv>
                            <LabelField fontSize={"1.5rem"} display={"flex"}>
                                대기중
                            </LabelField>
                        </ContentDiv>
                    </BombDiv>
                ):hostCheck&&roomStatus==="준비 완료"&&!gameStartClick?(
                    <BombDiv>
                        <ContentDiv>
                            <LabelField fontSize={"1.5rem"} display={"none"}>
                                시작!
                            </LabelField>
                        </ContentDiv>
                        <ContentDiv>
                            <BombImg src={bombImg} onClick={()=>hostStartGame()} />
                        </ContentDiv>
                    </BombDiv>
                ):(
                    <BombDiv>
                        <ContentDiv>
                            <LabelField fontSize={"1.5rem"} display={"flex"}>
                                {roomStatus}
                            </LabelField>
                        </ContentDiv>
                    </BombDiv>
                )}
			</VerticalDiv>
		</Container>
	);
}

const Container = styled.div`
	display: flex;
	flex-direction: column;
	background-color: #edefdf;
	margin: auto;
	width: 100vw;
	height: 100vh;
	vertical-align: middle;
	justify-content: center;
`;

const VerticalDiv = styled.div`
	display: flex;
	flex-direction: column;
	margin: auto;
	height: ${(props)=>props.height || "30%"};
	width: 100%;
	justify-content: center;
	vertical-align: middle;
	align-items: center;
`;

const VerticalDiv2 = styled.div`
	display: flex;
	flex-direction: column;
	margin: auto;
    height: ${(props)=>props.height || "30%"};
	width: 80%;
	justify-content: center;
	vertical-align: middle;
	align-items: center;
    border: 1px solid black;
    border-radius: 15px;
`;

const ScrollDiv = styled.div`
    display: flex;
	flex-direction: column;
	margin: auto;
    width: 100%;
    max-height: ${(props)=>props.maxHeight || "30%"};
    overflow: scroll;
    overflow-x: hidden;
    &::-webkit-scrollbar {
        width: 1rem;
        border-radius: 5px;
        background: #8B413A;
    }
    &::-webkit-scrollbar-thumb {
        background-color: #ED6F63;
        border-radius: 5px;
    }
`;


const ContentDiv = styled.div`
	display: flex;
	flex-direction: row;
	width: 100%;
	margin: 0.5rem;
	justify-content: center;
	vertical-align: middle;
	align-items: center;
`;

const LabelField = styled.div`
	display: ${(props)=>props.display || "flex"};
	margin: auto;
	font-family: var(--font-head);
	font-weight: 500;
	font-size: ${(props)=>props.fontSize || "2rem"};
	color: black;
	width: ${(props)=>props.width || "10rem"};
	vertical-align: middle;
	justify-content: center;
	align-items: center;
`;

const TextField = styled.input`
	display: flex;
	margin: auto;
	width: 10rem;
	height: 1.2rem;
	font-family: var(--font-main);
	border-radius: 5px;
	border-top: 1px solid #322180;
	border-bottom: 1px solid #322180;
	border-left: 1px solid #322180;
	border-right: 1px solid #322180;
`;

const BombDiv = styled.div`
	display: flex;
	flex-direction: column;
	margin: auto;
	vertical-align: middle;
	justify-content: center;
	align-items: center;
	cursor: pointer;
	&:hover{
		div{
			display: flex;
		}
		img {
			filter: invert(100%);
			-webkit-filter: invert(100%);
			
		}
	}
`;

const BombImg = styled.img`
	display: flex;
	width: 10rem;
	margin: auto;
	padding-left: 3.5rem;
	padding-bottom: 3.6rem;
	vertical-align: middle;
	justify-content: center;
	align-items: center;
`;