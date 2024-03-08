import { useState } from "react";
import styled from "styled-components"
import { LoginButton } from "./loginButton";
import Swal from 'sweetalert2';
import { useNavigate } from 'react-router-dom';
import heutonLogo from '../../assets/img/heuton_logo_gnb.png';
import axios from "axios";

export const LoginForm =()=> {
	const [id, setId] = useState("");
	const [pwd, setPwd] = useState("");
	const navigate = useNavigate();
	
	const loginEvent =async()=> {
		try {
			const response = await axios.post("");
			console.log(response);
			if(response?.status===200){
				const roomId = `${1234}`;
				window.sessionStorage.setItem('roomId', roomId);
				window.sessionStorage.setItem('loginStatus', true);
				Swal.fire({
					title: "반가워요 휴트너!",
					imageUrl: heutonLogo,
					imageAlt: "Heuton Logo",
					  imageHeight: 100,
					icon: "success",
					confirmButtonColor: '#8B413A',
				}).then(result => {
					if(result.isConfirmed) {
						navigate(`/onboarding`);
					}
				});
				
			} else {
				window.sessionStorage.setItem('roomId', false);
				window.sessionStorage.setItem('loginStatus', false);
				Swal.fire({
					title: "Oops... 휴트너가 아니신가요?",
					imageUrl: heutonLogo,
					imageAlt: "Heuton Logo",
					  imageHeight: 100,
					icon: "warning",
					showCancelButton: true,
					confirmButtonColor: '#8B413A',
					confirmButtonText: '저도 휴트너 할래요!',
					cancelButtonColor: '#8B413A',
					cancelButtonText: '휴튼은 뭐하는 곳인가요?'
				}).then(result => {
					if (result.isConfirmed) {
						window.open("");
					} else if (result.isDismissed && result.dismiss===Swal.DismissReason.cancel) {
						window.open("");
					}
				});
			}
		} catch {
			Swal.fire({
				title: "Oops... 휴트너가 아니신가요?",
				imageUrl: heutonLogo,
				imageAlt: "Heuton Logo",
  				imageHeight: 100,
				icon: "warning",
				showCancelButton: true,
				confirmButtonColor: '#8B413A',
				confirmButtonText: '저도 휴트너 할래요!',
				cancelButtonColor: '#8B413A',
				cancelButtonText: '휴튼은 뭐하는 곳인가요?'
			}).then(result => {
				if (result.isConfirmed) {
					window.open("");
				} else if (result.isDismissed && result.dismiss===Swal.DismissReason.cancel) {
					window.open("");
				}
			});
		}
	}

	const setIdEvent =(e)=> {
		setId(e.target.value);
	}

	const setPwdEvent =(e)=> {
		setPwd(e.target.value);
	}

	const handleOnKeyPress = (e) => {
		if (e.key === 'Enter') {
			loginEvent(id, pwd);
		}
	};

	return(
		<Container>
			<BorderedBox>
				<VerticalDiv>
					<ContentDiv>
						<LabelField>휴튼 로그인</LabelField>
					</ContentDiv>
				</VerticalDiv>
				<VerticalDiv>
					<ContentDiv>
						<LoginButton text={"로그인"} bgColor={"#8B413A"} hoverBgColor={"#db9a49"} onClick={()=>loginEvent(id, pwd)}/>
					</ContentDiv>
				</VerticalDiv>
			</BorderedBox>
		</Container>
	);
}

const Container = styled.div`
	display: flex;
  background-color: #341816;
	margin: auto;
	width: 15rem;
	height: 20rem;
  border: 3px solid #522622;
  border-radius: 15px;
`;

const VerticalDiv = styled.div`
	display: flex;
	flex-direction: column;
	margin: auto;
	height: 30%;
	justify-content: center;
	vertical-align: middle;
`;

const ContentDiv = styled.div`
	display: flex;
	flex-direction: row;
	margin: 0;
`;

const BorderedBox = styled.div`
	display: flex;
	flex-direction: column;
	background-color: #ED6F63;
	margin: auto;
	width: 90%;
	height: 90%;
	border: 2px solid #ffffff;
	border-radius: 10px;
	justify-content: center;
	vertical-align: middle;
`;

const LabelField = styled.div`
	display: flex;
	margin: auto;
	font-family: var(--font-head);
	font-weight: 500;
	font-size: 1.3rem;
	color: #ffffff;
`;

const TextField = styled.input`
	display: flex;
	margin: 0.5rem;
	width: 8rem;
	height: 1.2rem;
	font-family: var(--font-main);
	border-radius: 5px;
	border-top: 1px solid #322180;
	border-bottom: 1px solid #322180;
	border-left: 1px solid #322180;
	border-right: 1px solid #322180;
`;
