import { useState, useEffect, useRef } from "react";


export const useWs = (url, setData) => {
    const [isReady, setIsReady] = useState(false);
  
    const ws = useRef(null);
  
    useEffect(() => {
      const socket = new WebSocket(url);
  
      socket.onopen = () => setIsReady(true);
      socket.onclose = () => setIsReady(false);
      socket.onmessage = (event) => setData(JSON.parse(event.data)?.object);
  
      ws.current = socket;
  
      return () => {
        socket.close();
      }
    }, []);
  
    // bind is needed to make sure `send` references correct `this`
    return [isReady, ws.current?.send.bind(ws.current)];
  }