import { LoginForm } from "../component/login/loginForm";
import styled from "styled-components";


export const LoginPage =()=> {
	window.sessionStorage.setItem('loginStatus', false);
	window.sessionStorage.setItem('roomId', null);

	return(
		<Container>
			<LoginForm />
		</Container>
	);
}

const Container = styled.div`
	display: flex;
	flex-direction: column;
	background-color: #110807;
	margin: auto;
	width: 100vw;
	height: 100vh;
	vertical-align: middle;
	justify-content: center;
`;