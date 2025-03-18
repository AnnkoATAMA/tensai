import { Route, Routes } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import { useTemplateTheme } from "./utils/theme";

import LoginPage from "./pages/LoginPage.tsx";
import NotFoundPage from "./pages/NotFoundPage.tsx";
import HomePage from "./pages/HomePage.tsx";
import RegisterPage from "./pages/RegisterPage.tsx";
import RoomPage from "./pages/RoomPage.tsx";
import ProtectRoute from "./components/ProtectRoute.tsx";
import MatchPage from "./pages/MatchPage.tsx";


const App = () => {
    const theme = useTemplateTheme();
    return (
        <ThemeProvider theme={theme}>
            <CssBaseline />
            <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage/>} />
                <Route element={<ProtectRoute/>}>
                    <Route index element={ <HomePage />} />
                    <Route path="/room" element={<RoomPage />} />
                    <Route path="/room/:roomId" element={<MatchPage />} />
                </Route>
                <Route path="*" element={<NotFoundPage/>} />
            </Routes>
        </ThemeProvider>
    );
};

export default App;
