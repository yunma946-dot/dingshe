DINGSHE MOBILE CHAT BUTTON FIX
===============================

Files should be extracted directly into the dingshe-site project root.

Step 1 - Website
1. Double-click apply_mobile_chat_fix.bat.
2. Do NOT run the one-click website update command for this patch.

Step 2 - Chat server
1. Upload site1-mobile-chat-server-fix.tar.gz to /root on the server.
2. Run:

tar -xzf /root/site1-mobile-chat-server-fix.tar.gz -C /root
bash /root/site1-mobile-chat-server-fix/install.sh

Step 3 - Publish
Run the existing Upload-to-GitHub batch file in the project root.

This patch does not modify Excel, JSON, images, videos, or chat data.
