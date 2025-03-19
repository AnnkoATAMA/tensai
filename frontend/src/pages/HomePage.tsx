import {Link} from "react-router-dom";
import Logout from "../components/logout.tsx";
import { useEffect } from "react";
import "./homePage.css";
import {Box, Typography, Button} from "@mui/material";


const HomePage = () => {
    useEffect(() => {
        const binaryContainer = document.querySelector(".binary-background");

        if (binaryContainer) {
            for (let i = 0; i < 50; i++) {
                const binaryElement = document.createElement("div");
                binaryElement.classList.add("binary-number");
                binaryElement.innerText = Math.random() > 0.5 ? "1" : "0";
                binaryElement.style.left = `${Math.random() * 100}vw`;
                binaryElement.style.animationDuration = `${2 + Math.random() * 3}s`;
                binaryElement.style.animationDelay = `${Math.random() * 2}s`;
                binaryContainer.appendChild(binaryElement);
            }
        }
    }, []);

    return (

        <Box className="homepage-container">
            <Box className="binary-background"></Box>
            <Typography variant="h3" >Binary Mahjong</Typography>
            <Button component={Link} to="/room" sx={{color:"white"}}>Start</Button>

            <Logout />
        </Box>

    );
};

export default HomePage;