import { Suspense } from "react";
import Login from "../components/Login.tsx";
import {CircularProgress} from "@mui/material";

const LoginPage = () => {
    return (
        <Suspense fallback={<CircularProgress sx={{ display: 'block', mx: 'auto', mt: 4 }} />}>
            <Login />
        </Suspense>
    );
}

export default LoginPage;