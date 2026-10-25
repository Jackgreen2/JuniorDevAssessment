Junior Developer Assessment

Using python because of familiarity with restAPI and Jsonify which will cover message 
handling between client and server and JSON parsing. Using python will also improve 
readability of the codebase for reviewing

Structure:
Client-Server Architecture

Message Handling:
- Client sends request to server
- Server extracts order number from the message, checks whether it exists, applies the
cancellation policy. 
- Server then requests LLM to craft a message back to the user giving feedback on the
result of their request.

