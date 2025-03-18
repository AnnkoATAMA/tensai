import { useContext } from "react";
import { AuthContext } from "./AuthContext";
import { Button } from "@mui/material";

const Logout = () => {
    const { setIsAuthenticated } = useContext(AuthContext);

    const handleLogout = () => {
        document.cookie = "access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
        setIsAuthenticated(false);
    };

    return (
        <Button variant="contained" color="secondary" onClick={handleLogout}>
            Logout
        </Button>
    );
};

export default Logout;
