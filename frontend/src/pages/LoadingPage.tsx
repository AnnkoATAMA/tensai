import {Box, CircularProgress, Container} from "@mui/material";

const LoadingPage = () => {
    return (
        <Container>
            <Box>
                <CircularProgress/>
            </Box>
        </Container>
    )
}

export default LoadingPage;