import { useState } from "react";
import { GameOnboarding } from "../component/home/gameOnboarding"
import { GameLoading } from "../component/home/gameLoading"

export const OnboardingPage =()=> {
	const [loadingStatus, setLoadingStatus] = useState(true);

	if(loadingStatus){
		return(
			<GameLoading setLoadingStatus={setLoadingStatus} loadingTime={3000} blurTime={2000} blurVelocity={100} />
		);
	} else {
        return(
            <GameOnboarding />
        );
    }
}
