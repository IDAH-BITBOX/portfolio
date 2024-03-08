import { useState, useEffect } from "react";
import { useNavigate, Link } from 'react-router-dom';
import styled from "styled-components";
import bombImg from "../../assets/img/bomb.png";
import axios from "axios";


export const GameOnboarding =()=> {
	const navigate = useNavigate();
	const [roomIdOrigin, setRoomIdOrigin] = useState(null);
    const [roomMaxCnt, setRoomMaxCnt] = useState(2);
	const [roomTheme, setRoomTheme] = useState("");
	const [firstQuestion, setFirstQuestion] = useState("");
	const [gameOverTimer, setGameOverTimer] = useState(10);
	useEffect(() => {
		setRoomIdOrigin(window.sessionStorage.getItem('roomId'));
	  }, []);

    const setRoomMaxCntEvent =(e)=> {
		if(e.target.value<=8&&e.target.value>=2){
			setRoomMaxCnt(e.target.value);
		}
	}

	const setGameOverTimerEvent =(e)=> {
		if(e.target.value>=10){
			setGameOverTimer(e.target.value);
		}
	}

	const setRoomThemeEvent =(e)=> {
		setRoomTheme(e.target.value);
	}

	const setFirstQuestionEvent =(e)=> {
		setFirstQuestion(e.target.value);
	}

	const handleOnKeyPress = (e) => {
		if (e.key === 'Enter') {
			enterEvent();
		}
	};

    const enterEvent = async ()=> {
		if(gameOverTimer >= 10){
			window.sessionStorage.setItem('roomMaxCnt', roomMaxCnt);
			window.sessionStorage.setItem('roomTheme', roomTheme);
			window.sessionStorage.setItem('gameOverTimer', gameOverTimer);
			window.sessionStorage.setItem('firstQuestion', firstQuestion);
			
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
						room_theme:roomTheme,
						question:firstQuestion
					};
					const response = await axios.post(`/createRoom/${roomIdOrigin}/${roomMaxCnt}/${gameOverTimer}`,
						data,
						{
							headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
						}
					);
					console.log(response.data?.object);
					if(response.data?.hashedRoomId&&response.data?.status===200){
						navigate(`/progress/${response.data?.hashedRoomId}/${roomMaxCnt}/ready`);
					} else if(response.data?.status===404){
						alert(`질문 점수는 ${response.data?.object} 점입니다. 0.7 이 통과 점수 입니다.`);
					}
				} catch {
					alert("서버 오류!");
				}
			} catch {
				alert("서버 오류!");
			}
		} else {
			alert("게임 타이머가 너무 짧습니다! 10초 이상으로 설정해주세요.");
		}
    }
	if(window.sessionStorage.getItem('roomId')&&window.sessionStorage.getItem('loginStatus')){
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
							방 개설
						</LabelField>
					</ContentDiv>
				</VerticalDiv>
				<VerticalDiv height={"40%"}>
					<ContentDiv>
						<LabelField fontSize={"1.2rem"} width={"10rem"}>
							최대 수용 인원
						</LabelField>
						<TextField type={"number"} min={"2"} max={"8"} width={"10rem"} onChange={setRoomMaxCntEvent} value={roomMaxCnt} defaultValue={2} placeholder={2} onKeyPress={handleOnKeyPress}></TextField>
					</ContentDiv>
					<ContentDiv>
						<LabelField fontSize={"1.2rem"} width={"10rem"}>
							게임 타이머
						</LabelField>
						<TextField type={"number"} min={"10"} max={"60"} width={"10rem"} onChange={setGameOverTimerEvent} value={gameOverTimer} defaultValue={10} placeholder={10} onKeyPress={handleOnKeyPress}></TextField>
					</ContentDiv>
					<ContentDiv>
						<LabelField fontSize={"1.2rem"} width={"10rem"}>
							방의 키워드
						</LabelField>
						<TextField2 type={"text"} width={"10rem"} height={"2.4rem"} onChange={setRoomThemeEvent} onKeyPress={handleOnKeyPress}></TextField2>
					</ContentDiv>
					<ContentDiv>
						<LabelField fontSize={"1.2rem"} width={"10rem"}>
							첫 질문
						</LabelField>
						<TextField2 type={"text"} width={"10rem"} height={"2.4rem"} onChange={setFirstQuestionEvent} onKeyPress={handleOnKeyPress}></TextField2>
					</ContentDiv>
				</VerticalDiv>
				<VerticalDiv height={"40%"}>
					<BombDiv>
						<ContentDiv>
							<LabelField fontSize={"1.5rem"} display={"none"}>
								가즈아!
							</LabelField>
						</ContentDiv>
						<ContentDiv>
							<BombImg src={bombImg} onClick={()=>enterEvent()} />
						</ContentDiv>
					</BombDiv>
				</VerticalDiv>
			</Container>
		);
	} else {
		return(
			<Container>
				<VerticalDiv height={"100%"}>
					<ContentDiv>
						<LabelField fontSize={"1.5rem"} width={"15rem"}>
							<Link to={"/"} >로그인 하러 가기</Link>
						</LabelField>
					</ContentDiv>
				</VerticalDiv>
			</Container>
		);
	}
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
	display: block;
	margin: auto;
	width: ${(props)=>props.width || "10rem"};
	height: ${(props)=>props.height || "2rem"};
	font-family: var(--font-main);
	border-radius: 5px;
	border-top: 1px solid #322180;
	border-bottom: 1px solid #322180;
	border-left: 1px solid #322180;
	border-right: 1px solid #322180;
	text-align: center;
	font-size: 1.3rem;
`;

const TextField2 = styled.textarea`
	display: block;
	margin: auto;
	width: ${(props)=>props.width || "10rem"};
	height: ${(props)=>props.height || "1.2rem"};
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