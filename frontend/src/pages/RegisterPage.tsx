import { Suspense } from "react";
import {CircularProgress} from "@mui/material";
import Register from "../components/Register.tsx";


const RegisterPage = () => {
    return (
        <Suspense fallback={<CircularProgress sx={{ display: 'block', mx: 'auto', mt: 4 }} />}>
            <Register />
        </Suspense>
    );
}

export default RegisterPage;