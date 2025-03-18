import {Box, Container, Typography} from "@mui/material";
import Logout from "../components/logout.tsx"
import {Link} from "react-router-dom";

const HomePage = () => {
    return (
        <Container>
            <Box
                sx={{
                    display: "flex",
                    justifyContent: "center",
                    alignItems: "center",
                    height: "100vh",
                }}
            >
                <Typography>
                    hello
                </Typography>
                <Link to="/room">roomPage</Link>
                <Logout />
            </Box>
        </Container>
    )
}
export default HomePage;