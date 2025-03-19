import { Box, Button, Container, TextField, Typography } from "@mui/material";
import { useState, useContext } from "react";
import { Link, useNavigate, useLocation } from "react-router-dom";
import axios from "axios";
import { AuthContext } from "./AuthContext.tsx";

const loginUser = async (email: string, password: string) => {
    return axios.post("http://172.20.10.2:8000/api/user/login", { email, password }, { withCredentials: true });
};

const Login = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();
    const location = useLocation();
    const { setIsAuthenticated } = useContext(AuthContext);

    const handleLogin = async () => {
        try {
            await loginUser(email, password);
            setIsAuthenticated(true);
            const redirectPath = location.state?.redirectPath || "/";
            navigate(redirectPath);
        } catch (error) {
            console.error("ログイン失敗:", error);
        }
    };

    return (
        <Container maxWidth="xs" sx={{ mt: 8 }}>
            <Box>
                <Typography variant="h4" align="center" gutterBottom>
                    Login
                </Typography>
            </Box>
            <Box>
                <TextField
                    fullWidth
                    label="Email"
                    variant="outlined"
                    margin="normal"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                />
                <TextField
                    fullWidth
                    label="Password"
                    type="password"
                    variant="outlined"
                    margin="normal"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                <Button
                    fullWidth
                    variant="contained"
                    color="primary"
                    sx={{ mt: 2 }}
                    onClick={handleLogin}
                >
                    Login
                </Button>
                <Box alignItems="center" sx={{ mt: 2 }}>
                    <Link to="/register">新規登録はこちら</Link>
                </Box>
            </Box>
        </Container>
    );
};

export default Login;