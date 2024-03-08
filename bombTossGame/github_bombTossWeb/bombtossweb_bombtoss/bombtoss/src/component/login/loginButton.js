import styled from "styled-components";


export const LoginButton =({text, bgColor, hoverBgColor, onClick})=> {
	return(
		<Button bgColor={bgColor} hoverBgColor={hoverBgColor} onClick={onClick}>{text}</Button>
	);
}

const Button = styled.button`
  background-color: ${(props) => props.bgColor || "#FFFFFF"};
	width: 8rem;
	height: 2rem;
  border: 1px solid #FFFFFF;
  border-radius: 10px;
	font-family: var(--font-head);
	font-weight: 500;
	font-size: 1rem;
	color: #FFFFFF;
	cursor: pointer;
	transition: 0.2s;
	&:hover{
		box-shadow: 200px 0 0 0 ${(props) => props.hoverBgColor || "#FFFFFF"} inset, 
							 -200px 0 0 0 ${(props) => props.hoverBgColor || "#FFFFFF"} inset;
	}
`;