import { useState, useEffect } from "react";
import { GameLoading } from "../component/home/gameLoading"
import { GameEnd } from "../component/home/gameEnd"


export const EndPage =()=> {
	const [loadingStatus, setLoadingStatus] = useState(true);

	if(loadingStatus){
		return(
			<GameLoading setLoadingStatus={setLoadingStatus} loadingTime={3000} blurTime={2000} blurVelocity={100} />
		);
	} else {
		return(
			<GameEnd />
		);
	}
}