import { useState, useEffect } from "react";
import { useNavigate, useParams } from 'react-router-dom';
import styled from "styled-components";
import bombImg from "../../assets/img/bomb.png";

export const GameEnd =()=> {
	const navigate = useNavigate();
	const params = useParams();
	const roomIdOrigin = `${params.room_id}`;
    const roomMaxCnt = parseInt(`${params.room_max_cnt}`);
	const winnerNickname = `${params.winner_nickname}`;
	
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
						게임 종료!
					</LabelField>
				</ContentDiv>
			</VerticalDiv>
			<VerticalDiv height={"40%"}>
				<ContentDiv>
					<LabelField fontSize={"1.2rem"} width={"15rem"}>
						게임의 최종 승자는..
					</LabelField>
					<LabelField fontSize={"1.2rem"} width={"5rem"}>
						{winnerNickname}
					</LabelField>
				</ContentDiv>
			</VerticalDiv>
			<VerticalDiv height={"40%"}>
				<BombDiv>
					<ContentDiv>
						<LabelField fontSize={"1.5rem"} display={"flex"}>
							리겜 가즈아!
						</LabelField>
					</ContentDiv>
					<ContentDiv>
						{window.sessionStorage.getItem('loginStatus')&&window.sessionStorage.getItem('roomId')?<BombImg src={bombImg} onClick={()=>navigate(`/onboarding`)} />:<BombImg src={bombImg} onClick={()=>navigate(`/`)} />}
					</ContentDiv>
				</BombDiv>
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