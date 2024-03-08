import { LoginPage } from "./page/loginPage";
import { ReadyPage } from "./page/readyPage";
import { OngoingPage } from "./page/ongoingPage";
import { EndPage } from "./page/endPage";
import { OnboardingPage } from "./page/onboardingPage";
import { Routes,Route } from "react-router-dom";


export const App =()=> {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/onboarding" element={<OnboardingPage />} />
      <Route path="/progress/:room_id/:room_max_cnt/ready" element={<ReadyPage />} />
      <Route path="/progress/:room_id/:room_max_cnt/ongoing" element={<OngoingPage />} />
      <Route path="/progress/:room_id/:room_max_cnt/:winner_nickname/end" element={<EndPage />} />
    </Routes>
  );
}

export default App;
