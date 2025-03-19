import { use, useState} from "react";
import { useNavigate } from "react-router-dom";
import { Container, TextField, Button, Typography, Box } from "@mui/material";
import axios from "axios";

const registerUser = async (name: string, email: string, password: string) => {
    return axios.post("http://172.20.10.2:8000/api/user/register", { name, email, password }, { withCredentials: true });
};

const Register = () => {
    const [name, setName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleRegister = () => {
        const registerPromise = registerUser(name, email, password).then(() => {
            navigate("/login");
        });
        use(registerPromise);
    };

    return (
        <Container maxWidth="xs" sx={{ mt: 8 }}>
            <Box>
                <Typography variant="h4" align="center" gutterBottom>
                    Register
                </Typography>
            </Box>
            <Box>
                <TextField
                    fullWidth
                    label="Name"
                    variant="outlined"
                    margin="normal"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                />
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
                    onClick={handleRegister}
                >
                    Register
                </Button>
            </Box>
        </Container>
    );
};

export default Register;
