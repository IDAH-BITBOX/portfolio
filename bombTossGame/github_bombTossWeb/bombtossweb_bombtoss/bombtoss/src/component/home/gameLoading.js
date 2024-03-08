import { useState, useEffect } from "react";
import styled from "styled-components";
import heutonLogo from '../../assets/img/heuton_logo_gnb.png'

export const GameLoading =({ setLoadingStatus, loadingTime, blurTime, blurVelocity })=> {
	const [blurStatus, setBlurStatus] = useState(0);
	const [timeCnt, setTimeCnt] = useState(0);

	useEffect(()=>{
    	var timer2 = setTimeout(()=>{ setLoadingStatus(false) }, loadingTime);
		var timer3 = setTimeout(()=>{ setTimeCnt(timeCnt + 1) }, 1);
  });

	useEffect(()=>{
		if(timeCnt > loadingTime - blurTime && blurStatus < blurVelocity / 5) {
			var timer1 = setTimeout(()=>{ setBlurStatus(blurStatus + 1) }, blurVelocity - 5 * blurStatus);
		}
	}, [timeCnt]);

	return(
		<Container blur={`blur(${blurStatus}px)`}>
		</Container>
	)
}

const Container = styled.div`
	display: flex;
	flex-direction: column;
	background-color: #edefdf;
	background-image: url(${heutonLogo});
	background-position: center;
	background-size: 30%;
	background-repeat: no-repeat;
	margin: auto;
	width: 100vw;
	height: 100vh;
	vertical-align: middle;
	justify-content: center;
	align-items: center;
	filter: ${(props)=>props.blur || "blur(0px)"};
  -webkit-filter: ${(props)=>props.blur || "blur(0px)"};
`;