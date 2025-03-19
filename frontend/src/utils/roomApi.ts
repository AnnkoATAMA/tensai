import axios from "axios";

const API_URL = "http://172.20.10.2:8000";

export const fetchRooms = async () => {
    return axios.get(`${API_URL}/room`, { withCredentials: true })
        .then(res => res.data);
};

// export const updateRoom = async (roomId: number, gameType: string, maxPlayers: number) => {
//     return axios.put(`${API_URL}/room/${roomId}`,
//         { game_type: gameType, max_players: maxPlayers },
//         { withCredentials: true }
//     );
// };

export const createRoom = async (gameType: string) => {
    let maxPlayers = gameType === "sanma" ? 3 : 4;
    return axios.post(`${API_URL}/room`, { max_players: maxPlayers, game_type: gameType }, { withCredentials: true });
};

export const deleteRoom = async (roomId: number) => {
    return axios.delete(`${API_URL}/room/${roomId}`, { withCredentials: true });
};

export const joinRoom = async (roomId: number) => {
    return axios.post(`${API_URL}/room/${roomId}/join`, {}, { withCredentials: true });
};

export const leaveRoom = async (roomId: number) => {
    return axios.delete(`${API_URL}/room/${roomId}/leave`, { withCredentials: true });
};

export const fetchRoomPlayers = async (roomId: number) => {
    return axios.get(`${API_URL}/room/${roomId}/players`, { withCredentials: true })
        .then(res => res.data);
};
