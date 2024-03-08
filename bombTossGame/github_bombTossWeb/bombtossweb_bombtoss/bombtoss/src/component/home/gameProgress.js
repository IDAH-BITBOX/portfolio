import { useState, useEffect } from "react";
import { useParams, Link, useNavigate } from 'react-router-dom';
import styled from "styled-components";
import backgroundImg from "../../assets/img/tossbomb_8.png";
import bombImg from "../../assets/img/bomb.png";
import { SubmitButton } from "../../component/home/submitButton";
import { GameLoading } from "./gameLoading"
import axios from "axios";
import { useWs } from "../hook/webSocket";
import Swal from 'sweetalert2';
import heutonLogo from '../../assets/img/heuton_logo_gnb.png'


export const GameProgress =()=> {
	const navigate = useNavigate();
	const myNickname = window.sessionStorage.getItem('nickname');
	const [answer, setAnswer] = useState("");
	const [answerCheck, setAnswerCheck] = useState(false);
	const [question, setQuestion] = useState("");
	const [questionCheck, setQuestionCheck] = useState(false);
	const [roomTheme, setRoomTheme] = useState("");
	const [loadingStatus, setLoadingStatus] = useState(false);
	const params = useParams();
	const roomIdOrigin = `${params.room_id}`;
    const roomMaxCnt = parseInt(`${params.room_max_cnt}`);
	const [data, setData] = useState({
		frontData:{},
		frontUserData:[],
	});
	const maxTimer = 10000;
	const [timer, setTimer] = useState(0);
	const [fetchBlock, setFetchBlock] = useState(false);
	const [dataReady, dataSend] = useWs(`ws://bitbox.iptime.org:9091/ws/gameProgress`, setData);

	useEffect(()=>{
		console.log(timer);
		var timeout = setTimeout(()=>fetchData(), 1000);
	},[timer]);

	useEffect(() => {
		window.sessionStorage.setItem('firstQuestion', null);
		if(dataReady) {
			initFetchData();
		}
  	}, [roomIdOrigin, dataReady]);

	useEffect(() => {
		if(data?.frontData?.curr_timer==0 && data?.frontData?.curr_nickname===myNickname){
			gameOverEvent();
		}
	}, [data?.frontData?.curr_timer]);

	const initFetchData =async()=> {
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
				const response = await axios.get(`/getGameDataInfo/${roomIdOrigin}`,
					{
						headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
					}
				);
				const data_ = {
					roomId:roomIdOrigin,
					currNickname:response.data?.object.curr_nickname,
					currPosition:response.data?.object.curr_position,
					currQuestion:response.data?.object.curr_question,
					currAnswer:response.data?.object.curr_answer,
					currRound:response.data?.object.curr_round,
					currTimer:response.data?.object.curr_timer,
				};
				dataSend(JSON.stringify(data_));
				try {
					const response2 = await axios.get(`/roomUserInfo/${roomIdOrigin}`,
						{
							headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
						}
					);
					const data_0 = {
						frontData:response.data?.object,
						frontUserData:response2.data?.object,
					}
					setData(data_0);
					/*const data_ = {
						roomId:roomIdOrigin,
						currNickname:data_0?.frontData.curr_nickname,
						currPosition:data_0?.frontData.curr_position,
						currQuestion:data_0?.frontData.curr_question,
						currAnswer:data_0?.frontData.curr_answer,
						currRound:data_0?.frontData.curr_round,
						currTimer:data_0?.frontData.curr_timer,
					};
					try {
						const response = await axios.post(`/gameProgressResult/${roomIdOrigin}`,
						data_);
						//setTimer((timer+1)%roomMaxCnt);
					} catch {
						alert("서버 오류!");
					}*/
				} catch {
					Swal.fire({
						title: "Oops... 서버가 맛탱이가 갔나봐요!",
						imageUrl: heutonLogo,
						imageAlt: "Heuton Logo",
					  	imageHeight: 50,
						icon: "warning",
						showCancelButton: true,
						confirmButtonColor: '#8B413A',
						confirmButtonText: '문의하기',
						cancelButtonColor: '#8B413A',
						cancelButtonText: '확인',
					}).then(result => {
						if (result.isConfirmed) {
							window.open("");
						}
					});
				}
			} catch {
				Swal.fire({
					title: "Oops... 서버가 맛탱이가 갔나봐요!",
					imageUrl: heutonLogo,
					imageAlt: "Heuton Logo",
					  imageHeight: 50,
					icon: "warning",
					showCancelButton: true,
					confirmButtonColor: '#8B413A',
					confirmButtonText: '문의하기',
					cancelButtonColor: '#8B413A',
					cancelButtonText: '확인',
				}).then(result => {
					if (result.isConfirmed) {
						window.open("");
					}
				});
			}
		} catch {
			Swal.fire({
				title: "Oops... 서버가 맛탱이가 갔나봐요!",
				imageUrl: heutonLogo,
				imageAlt: "Heuton Logo",
				  imageHeight: 50,
				icon: "warning",
				showCancelButton: true,
				confirmButtonColor: '#8B413A',
				confirmButtonText: '문의하기',
				cancelButtonColor: '#8B413A',
				cancelButtonText: '확인',
			}).then(result => {
				if (result.isConfirmed) {
					window.open("");
				}
			});
		}
	}
	//console.log(myNickname, data?.frontData, data?.frontUserData.filter((row)=>row.status==="게임중"&&row.nickname===data?.frontData.curr_nickname&&row.nickname===myNickname)?.length);

	const fetchData =async()=> {
		console.log(fetchBlock);
		if(!fetchBlock){
			if(data?.frontUserData.filter((row)=>row.status==="게임중").length===1){
				const winnerNickname = data?.frontUserData.filter((row)=>row.status==="게임중")[0].nickname;
				navigate(`/progress/${roomIdOrigin}/${roomMaxCnt}/${winnerNickname}/end`);
			}
			console.log(myNickname, data?.frontData, data?.frontUserData.filter((row)=>row.status==="게임중"&&row.nickname===data?.frontData.curr_nickname&&row.nickname===myNickname)?.length);
			if(data?.frontUserData.filter((row)=>row.status==="게임중"&&row.nickname===data?.frontData.curr_nickname&&row.nickname===myNickname)?.length>0){
				const data_ = {
					roomId:roomIdOrigin,
					currNickname:data?.frontData.curr_nickname,
					currPosition:data?.frontData.curr_position,
					currQuestion:data?.frontData.curr_question,
					currAnswer:answer,
					currRound:data?.frontData.curr_round,
					currTimer:data?.frontData.curr_timer - 1>=0?data?.frontData.curr_timer - 1:0,
				};
				try {
					const response = await axios.post(`/gameProgressResult/${roomIdOrigin}`,
					data_);
					setTimer((timer+2)%maxTimer);
				} catch {
					Swal.fire({
						title: "Oops... 서버가 맛탱이가 갔나봐요!",
						imageUrl: heutonLogo,
						imageAlt: "Heuton Logo",
					  	imageHeight: 50,
						icon: "warning",
						showCancelButton: true,
						confirmButtonColor: '#8B413A',
						confirmButtonText: '문의하기',
						cancelButtonColor: '#8B413A',
						cancelButtonText: '확인',
					}).then(result => {
						if (result.isConfirmed) {
							window.open("");
						}
					});
				}
			} else {
				//setQuestionCheck(false);
				//setAnswerCheck(false);
				setTimer((timer+2)%maxTimer);
			}
		}
	}

	const setAnswerEvent =(e)=> {
		setAnswer(e.target.value);
	}

	const setQuestionEvent =(e)=> {
		setQuestion(e.target.value);
	}

	const handleOnKeyPressAnswer = (e) => {
		if (e.key === 'Enter') {
			submitAnswer(answer);
		}
	};

	const handleOnKeyPressQuestion = (e) => {
		if (e.key === 'Enter') {
			submitQuestion(question);
		}
	};

	const submitAnswer =async(a)=> {
		setFetchBlock(true);
		setLoadingStatus(true);
		setAnswerCheck(true);
		setQuestionCheck(false);
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
				const data_ = {
					question:data?.frontData?.curr_question,
					answer:a
				};
				const response = await axios.post(`/gameAnswerCheck/${roomIdOrigin}`,
					data_,
					{
						headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
					}
				);
				//response.data?.object[0] > 0.5 && 
				if(response.data?.object[1] > 0.5){
					const data_ = {
						roomId:roomIdOrigin,
						currNickname:data?.frontData.curr_nickname,
						currPosition:data?.frontData.curr_position,
						currQuestion:data?.frontData.curr_question,
						currAnswer:a,
						currRound:data?.frontData.curr_round,
						currTimer:-100,
					};
					try {
						const response = await axios.post(`/gameProgressResult/${roomIdOrigin}`,
						data_);
						setAnswerCheck(true);
						setQuestionCheck(false);
						setFetchBlock(false);
						setTimer((timer+5)%maxTimer);
					} catch {
						Swal.fire({
							title: "Oops... 서버가 맛탱이가 갔나봐요!",
							imageUrl: heutonLogo,
							imageAlt: "Heuton Logo",
							  imageHeight: 50,
							icon: "warning",
							showCancelButton: true,
							confirmButtonColor: '#8B413A',
							confirmButtonText: '문의하기',
							cancelButtonColor: '#8B413A',
							cancelButtonText: '확인',
						}).then(result => {
							if (result.isConfirmed) {
								window.open("");
							}
							setAnswerCheck(false);
							setQuestionCheck(false);
							setFetchBlock(false);
							setTimer((timer+5)%maxTimer);
						});
					}
					/*const sendFrontData = {
						currNickname:data?.frontData?.curr_nickname,
						currPosition:data?.frontData?.curr_position,
						currQuestion:data?.frontData?.curr_question,
						currAnswer:a,
						currRound:data?.frontData?.curr_round,
						currTimer:-100,
					};
		
					try{
						const response3 = await axios.post(`/updateGameDataInfo/${roomIdOrigin}`,
							sendFrontData,
							{
								headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
							}
						);
						
						setAnswerCheck(true);
						setQuestionCheck(false);
					} catch {
						alert("서버 오류! 게임 업데이트");
						setAnswerCheck(false);
						setQuestionCheck(false);
					}*/
				} else{
					Swal.fire({
						title: "질문에 맞는 답변이 아니에요!",
						imageUrl: heutonLogo,
						imageAlt: "Heuton Logo",
					  	imageHeight: 50,
						icon: "warning",
						showCancelButton: false,
						confirmButtonColor: '#8B413A',
						confirmButtonText: '확인',
					}).then(result => {
						setAnswerCheck(false);
						setQuestionCheck(false);
						setFetchBlock(false);
						setTimer((timer+7)%maxTimer);
					});
				}
			} catch {
				Swal.fire({
					title: "Oops... 서버가 맛탱이가 갔나봐요!",
					imageUrl: heutonLogo,
					imageAlt: "Heuton Logo",
					  imageHeight: 50,
					icon: "warning",
					showCancelButton: true,
					confirmButtonColor: '#8B413A',
					confirmButtonText: '문의하기',
					cancelButtonColor: '#8B413A',
					cancelButtonText: '확인',
				}).then(result => {
					if (result.isConfirmed) {
						window.open("");
					}
					setAnswerCheck(false);
					setQuestionCheck(false);
					setFetchBlock(false);
					setTimer((timer+5)%maxTimer);
				});
			}
		} catch {
			Swal.fire({
				title: "Oops... 서버가 맛탱이가 갔나봐요!",
				imageUrl: heutonLogo,
				imageAlt: "Heuton Logo",
				  imageHeight: 50,
				icon: "warning",
				showCancelButton: true,
				confirmButtonColor: '#8B413A',
				confirmButtonText: '문의하기',
				cancelButtonColor: '#8B413A',
				cancelButtonText: '확인',
			}).then(result => {
				if (result.isConfirmed) {
					window.open("");
				}
				setAnswerCheck(false);
				setQuestionCheck(false);
				setFetchBlock(false);
				setTimer((timer+5)%maxTimer);
			});
		}
	}

	const submitQuestion =async(q)=> {
		setFetchBlock(true);
		setLoadingStatus(true);
		setAnswerCheck(true);
		setQuestionCheck(true);
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
				const data_ = {
					past_question:data?.frontData?.curr_question,
					question:q
				};
				const response = await axios.post(`/gameQuestionCheck/${roomIdOrigin}`,
					data_,
					{
						headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
					}
				);
				if(response.data?.object[0] > 0.7 && response.data?.object[1] < 0.7){
					const myPosition = data?.frontUserData.filter((row)=>row.nickname===myNickname)[0]?.position;
					const currNickname_ = data?.frontUserData.filter((row)=>row.position===(myPosition+1)%data?.frontUserData.filter((row)=>row.status==="게임중").length);
					
					/*const data_ = {
						currNickname:currNickname_[0]?.nickname,
						currPosition:(myPosition+1)%data?.frontUserData.filter((row)=>row.status==="게임중").length,
						currQuestion:q,
						currAnswer:"",
						currRound:data?.frontData.curr_round,
						currTimer:-200,
					};
					try {
						const response = await axios.post(`/gameProgressResult/${roomIdOrigin}`,
						data_);
						setAnswerCheck(true);
						setQuestionCheck(true);
					} catch {
						alert("서버 오류!");
						setAnswerCheck(true);
						setQuestionCheck(false);
					}*/

					const sendFrontData = {
						currNickname:currNickname_[0]?.nickname,
						currPosition:(myPosition+1)%data?.frontUserData.filter((row)=>row.status==="게임중").length,
						currQuestion:q,
						currAnswer:"",
						currRound:data?.frontData?.curr_round,
						currTimer:-200,
					};
					try{
						const response3 = await axios.post(`/gameProgressResult/${roomIdOrigin}`,
							sendFrontData);
						setQuestionCheck(false);
						setAnswerCheck(false);
						setAnswer("");
						setFetchBlock(false);
						setTimer((timer+3)%maxTimer);
					} catch {
						Swal.fire({
							title: "Oops... 서버가 맛탱이가 갔나봐요!",
							imageUrl: heutonLogo,
							imageAlt: "Heuton Logo",
							  imageHeight: 50,
							icon: "warning",
							showCancelButton: true,
							confirmButtonColor: '#8B413A',
							confirmButtonText: '문의하기',
							cancelButtonColor: '#8B413A',
							cancelButtonText: '확인',
						}).then(result => {
							if (result.isConfirmed) {
								window.open("");
							}
							setAnswerCheck(true);
							setQuestionCheck(false);
							setFetchBlock(false);
							setTimer((timer+5)%maxTimer);
						});
					}
				} else{
					Swal.fire({
						title: "방의 키워드에 맞지 않는 질문인가봐요!",
						imageUrl: heutonLogo,
						imageAlt: "Heuton Logo",
					  	imageHeight: 50,
						icon: "warning",
						showCancelButton: false,
						confirmButtonColor: '#8B413A',
						confirmButtonText: '확인',
					}).then(result => {
						setAnswerCheck(true);
						setQuestionCheck(false);
						setFetchBlock(false);
						setTimer((timer+7)%maxTimer);
					});
				}
			} catch {
				Swal.fire({
					title: "Oops... 서버가 맛탱이가 갔나봐요!",
					imageUrl: heutonLogo,
					imageAlt: "Heuton Logo",
					  imageHeight: 50,
					icon: "warning",
					showCancelButton: true,
					confirmButtonColor: '#8B413A',
					confirmButtonText: '문의하기',
					cancelButtonColor: '#8B413A',
					cancelButtonText: '확인',
				}).then(result => {
					if (result.isConfirmed) {
						window.open("");
					}
					setAnswerCheck(true);
					setQuestionCheck(false);
					setFetchBlock(false);
					setTimer((timer+5)%maxTimer);
				});
			}
		} catch {
			Swal.fire({
				title: "Oops... 서버가 맛탱이가 갔나봐요!",
				imageUrl: heutonLogo,
				imageAlt: "Heuton Logo",
				  imageHeight: 50,
				icon: "warning",
				showCancelButton: true,
				confirmButtonColor: '#8B413A',
				confirmButtonText: '문의하기',
				cancelButtonColor: '#8B413A',
				cancelButtonText: '확인',
			}).then(result => {
				if (result.isConfirmed) {
					window.open("");
				}
				setAnswerCheck(true);
				setQuestionCheck(false);
				setFetchBlock(false);
				setTimer((timer+5)%maxTimer);
			});
		}
	}

	const gameOverEvent =async()=> {
		setAnswerCheck(true);
		setQuestionCheck(true);
		var sendFrontUserData = {bulk:[]};
		var i;
		const myPosition = data?.frontUserData.filter((row)=>row.nickname===myNickname)[0]?.position;
		
		for(i=0; i<data?.frontUserData.length; i++){
			if(data?.frontUserData[i].nickname===myNickname){
				sendFrontUserData.bulk = sendFrontUserData.bulk.concat({
					nickname:data?.frontUserData[i].nickname,
					status:"게임 오버",
					position:-1,
				});
			} else{
				sendFrontUserData.bulk = sendFrontUserData.bulk.concat({
					nickname:data?.frontUserData[i].nickname,
					status:data?.frontUserData[i].status,
					position:data?.frontUserData[i].position>myPosition?data?.frontUserData[i].position-1:data?.frontUserData[i].position,
				});
			}
		}
		const currNickname_ = sendFrontUserData.bulk.filter((row)=>row.position===(myPosition+1)%sendFrontUserData.bulk.filter((row)=>row.status==="게임중").length);
		const sendFrontData = {
			currNickname:currNickname_.length?currNickname_[0]?.nickname:data?.frontData?.curr_nickname,
			currPosition:(myPosition+1)%sendFrontUserData.bulk.filter((row)=>row.status==="게임중").length,
			currQuestion:data?.frontData?.curr_question,
			currAnswer:"",
			currRound:data?.frontData?.curr_round,
			currTimer:-200,
		};

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
			try{
				const response2 = await axios.post(`/gameUserUpdate/${roomIdOrigin}`,
					sendFrontUserData,
					{
						headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
					}
				);
				try{
					const response3 = await axios.post(`/updateGameDataInfo/${roomIdOrigin}`,
						sendFrontData,
						{
							headers: {Authorization: `Bearer ${token_response.data?.access_token}`},
						}
					);
					
				} catch {
					Swal.fire({
						title: "Oops... 서버가 맛탱이가 갔나봐요!",
						imageUrl: heutonLogo,
						imageAlt: "Heuton Logo",
						  imageHeight: 50,
						icon: "warning",
						showCancelButton: true,
						confirmButtonColor: '#8B413A',
						confirmButtonText: '문의하기',
						cancelButtonColor: '#8B413A',
						cancelButtonText: '확인',
					}).then(result => {
						if (result.isConfirmed) {
							window.open("");
						}
					});
				}
			} catch {
				Swal.fire({
					title: "Oops... 서버가 맛탱이가 갔나봐요!",
					imageUrl: heutonLogo,
					imageAlt: "Heuton Logo",
					  imageHeight: 50,
					icon: "warning",
					showCancelButton: true,
					confirmButtonColor: '#8B413A',
					confirmButtonText: '문의하기',
					cancelButtonColor: '#8B413A',
					cancelButtonText: '확인',
				}).then(result => {
					if (result.isConfirmed) {
						window.open("");
					}
				});
			}
		} catch {
			Swal.fire({
				title: "Oops... 서버가 맛탱이가 갔나봐요!",
				imageUrl: heutonLogo,
				imageAlt: "Heuton Logo",
				  imageHeight: 50,
				icon: "warning",
				showCancelButton: true,
				confirmButtonColor: '#8B413A',
				confirmButtonText: '문의하기',
				cancelButtonColor: '#8B413A',
				cancelButtonText: '확인',
			}).then(result => {
				if (result.isConfirmed) {
					window.open("");
				}
			});
		}
	}
	if(loadingStatus){
		return(
			<Container>
				<VerticalDiv height={"10%"}>
					<ContentDiv>
						<LabelField width={"100%"}>
							질문 폭탄 게임
						</LabelField>
					</ContentDiv>
				</VerticalDiv>
				<VerticalDiv height={"10%"}>
					<ContentDiv>
						<LabelField width={"100%"}>
							키워드
						</LabelField>
						<LabelField fontSize={"1.2rem"} width={"100%"}>
							{roomTheme}
						</LabelField>
					</ContentDiv>
				</VerticalDiv>
				<VerticalDiv>
					<GameLoading setLoadingStatus={setLoadingStatus} loadingTime={2000} blurTime={1000} blurVelocity={400} />
				</VerticalDiv>
				<VerticalDiv>

				</VerticalDiv>
			</Container>
		);
	} else {
		if(myNickname||true){
			return(
				<Container>
					<VerticalDiv height={"2.5rem"}>
						<ContentDiv>
							<LabelField width={"100%"}>
								{myNickname?`질문 폭탄 게임`:`질문 폭탄 게임 (관전중)`}
							</LabelField>
						</ContentDiv>
					</VerticalDiv>
					<VerticalDiv height={"1.5rem"}>
						<ContentDiv>
							<LabelField fontSize={"1.2rem"} width={"20%"}>
								키워드
							</LabelField>
							<LabelField fontSize={"1.2rem"} width={"80%"}>
								{roomTheme}
							</LabelField>
						</ContentDiv>
					</VerticalDiv>
					<VerticalDiv height={"2.5rem"}>
						<ContentDiv>
							<LabelField fontSize={"1.1rem"} width={"20%"}>
								현재 질문
							</LabelField>
							<LabelField fontSize={"1.1rem"} width={"80%"}>
								{data?.frontData?.curr_question}
							</LabelField>
						</ContentDiv>
					</VerticalDiv>
					<VerticalDiv height={"2.5rem"}>
						<ContentDiv>
							<LabelField fontSize={"1.1rem"} width={"20%"}>
								현재 답변
							</LabelField>
							<LabelField fontSize={"1.1rem"} width={"80%"}>
								{data?.frontData?.curr_answer}
							</LabelField>
						</ContentDiv>
					</VerticalDiv>
					<VerticalDiv height={"30%"}>
						<GameViewDiv blur={"blur(2px)"}>
						</GameViewDiv>
						<BombImg src={bombImg} imgSize={"10rem"} marginLeft={"3.5rem"} marginBottom={"4rem"} />
					</VerticalDiv>
					{myNickname===data?.frontData?.curr_nickname&&data?.frontUserData.filter((row)=>row.nickname===myNickname)[0]?.status==="게임중"&&!answerCheck&&!questionCheck?(
						<VerticalDiv height={"20%"}>
							<ContentDiv>
								<LabelField width={"100%"}>
									{data?.frontData?.curr_timer}
								</LabelField>
							</ContentDiv>
							<ContentDiv>
								<LabelField fontSize={"1.2rem"} width={"4rem"}>
									질문:&nbsp; 
								</LabelField>
								<LabelField fontSize={"1.2rem"}  width={"20rem"}>
									{data?.frontData?.curr_question}
								</LabelField>
							</ContentDiv>
							<ContentDiv>
								<LabelField fontSize={"1.2rem"} width={"4rem"}>
									답변:&nbsp; 
								</LabelField>
								<TextField2 type="text" onChange={setAnswerEvent} onKeyPress={handleOnKeyPressAnswer}>
								</TextField2>
							</ContentDiv>
							<SubmitButton text={"답변 제출"} bgColor={"#8B413A"} hoverBgColor={"#db9a49"} onClick={()=>submitAnswer(answer)}/>
						</VerticalDiv>
					):myNickname===data?.frontData?.curr_nickname&&data?.frontUserData.filter((row)=>row.nickname===myNickname)[0]?.status==="게임중"&&!questionCheck&&answerCheck?(
						<VerticalDiv height={"20%"}>
							<ContentDiv>
								<LabelField width={"100%"}>
									{data?.frontData?.curr_timer}
								</LabelField>
							</ContentDiv>
							<ContentDiv>
								<LabelField fontSize={"1.2rem"} width={"4rem"}>
									질문:&nbsp; 
								</LabelField>
								<TextField2 type="text" onChange={setQuestionEvent} onKeyPress={handleOnKeyPressQuestion}>
								</TextField2>
							</ContentDiv>
							<SubmitButton text={"질문 제출"} bgColor={"#8B413A"} hoverBgColor={"#db9a49"} onClick={()=>submitQuestion(question)}/>
						</VerticalDiv>
					):data?.frontUserData.filter((row)=>row.nickname===myNickname)[0]?.status==="게임 오버"?(
						<VerticalDiv height={"20%"}>
							<ContentDiv>
								<LabelField width={"100%"}>
									게임 오버
								</LabelField>
							</ContentDiv>
						</VerticalDiv>
					):questionCheck&&answerCheck?(
						<VerticalDiv height={"20%"}>
							<ContentDiv>
								<LabelField width={"100%"}>
									대기중
								</LabelField>
							</ContentDiv>
						</VerticalDiv>
					):(
						<VerticalDiv height={"20%"}>
							<ContentDiv>
								<LabelField width={"50%"}>
									{data?.frontData?.curr_nickname}
								</LabelField>
								<LabelField width={"50%"}>
									{data?.frontData?.curr_timer}
								</LabelField>
							</ContentDiv>
						</VerticalDiv>
					)}
				</Container>
			);
		} else{
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
	display: flex;
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
	width: 20rem;
	height: 1.2rem;
	font-family: var(--font-main);
	border-radius: 5px;
	border-top: 1px solid #322180;
	border-bottom: 1px solid #322180;
	border-left: 1px solid #322180;
	border-right: 1px solid #322180;
`;

const TextField2 = styled.textarea`
	display: block;
	margin: auto;
	width: ${(props)=>props.width || "20rem"};
	height: ${(props)=>props.height || "2.4rem"};
	font-family: var(--font-main);
	border-radius: 5px;
	border-top: 1px solid #322180;
	border-bottom: 1px solid #322180;
	border-left: 1px solid #322180;
	border-right: 1px solid #322180;
`;

const GameViewDiv = styled.div`
	display: flex;
	flex-direction: column;
	background-color: #edefdf;
	background-image: url(${backgroundImg});
	background-position: center;
	background-size: 100%;
	background-repeat: no-repeat;
	filter: ${(props)=>props.blur || "blur(1px)"};
  -webkit-filter: ${(props)=>props.blur || "blur(1px)"};
	margin: auto;
	width: 20rem;
	height: 100%;
	vertical-align: middle;
	justify-content: center;
	align-items: center;
`;

const BombImg = styled.img`
	display: flex;
	position: absolute;
	width: ${(props)=>props.imgSize || "10rem"};
	margin-left: ${(props)=>props.marginLeft || "3.5rem"};;
	margin-bottom: ${(props)=>props.marginBottom || "3.7rem"};;
`;