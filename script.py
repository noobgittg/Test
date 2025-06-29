class Script(object):
    START_TXT = """<b>👋 Hello {},
I'm an advanced Auto Filter Bot with 4 database support!

🚀 Features:
• Lightning fast search
• 4 database redundancy
• Smart caching system
• IMDB integration
• Spell check
• High performance indexing

Send me any movie/series name to search!</b>"""

    HELP_TXT = """<b>🔥 Auto Filter Bot Help</b>

<b>🔍 How to search:</b>
• Just send movie/series name
• Bot will show available files
• Click on file to get it in PM

<b>👨‍💼 Admin Commands:</b>
• <code>/index [channel]</code> - Index files from channel
• <code>/stats</code> - Get database statistics
• <code>/broadcast</code> - Broadcast message to users

<b>⚙️ Features:</b>
• 4 Database support for redundancy
• Redis caching for fast responses
• IMDB movie information
• Smart spell checking
• Pagination for large results
• File type filtering

<b>📞 Support:</b> Contact admin for any issues"""

    ABOUT_TXT = """<b>📖 About Auto Filter Bot</b>

<b>🤖 Bot Name:</b> Auto Filter Bot
<b>📝 Language:</b> Python 3.9+
<b>📚 Framework:</b> Pyrogram
<b>💾 Database:</b> MongoDB (4x redundancy)
<b>🗄️ Cache:</b> Redis
<b>📡 Server:</b> VPS/Cloud

<b>🚀 Performance Features:</b>
• Multi-database architecture
• Intelligent caching system
• Concurrent search processing
• Optimized indexing
• Load balancing

<b>👨‍💻 Developer:</b> @YourUsername"""

    MANUELFILTER_TXT = """<b>Manual Filter Help</b>

<b>How to add manual filters:</b>
• Go to your group
• Send <code>/filter keyword reply_text</code>
• Bot will save the filter

<b>Example:</b>
<code>/filter hello Hi there! How are you?</code>

<b>Supported formats:</b>
• Text messages
• Media files
• Buttons with markdown

<b>To delete:</b>
<code>/delfilter keyword</code>

<b>View all filters:</b>
<code>/filters</code>"""

    BUTTON_TXT = """<b>Button Format Help</b>

<b>For inline buttons:</b>
<code>[Button Text](buttonurl:https://example.com)</code>

<b>For multiple buttons:</b>
<code>[Button 1](buttonurl:https://example.com)
[Button 2](buttonurl:https://example2.com)</code>

<b>For same row buttons:</b>
<code>[Button 1](buttonurl:https://example.com:same)
[Button 2](buttonurl:https://example2.com)</code>

<b>Example filter with button:</b>
<code>/filter movie Here is your movie!
[Download](buttonurl:https://example.com)
[Watch Online](buttonurl:https://stream.com)</code>"""

    AUTOFILTER_TXT = """<b>🔥 Auto Filter Help</b>

<b>How it works:</b>
• Send any movie/series name in group
• Bot automatically searches in database
• Shows available files with buttons
• Click to get file in PM

<b>🎯 Search Tips:</b>
• Use proper movie names
• Include year for better results
• Try different keywords if no results
• Check spelling

<b>⚡ Performance:</b>
• 4 database redundancy
• Smart caching system
• Sub-second response time
• Handles 1000+ concurrent users

<b>🎬 IMDB Integration:</b>
• Automatic movie info
• Ratings and plot
• Genre information
• Release year"""

    CONNECTION_TXT = """<b>🔗 Connection Help</b>

<b>How to connect your group:</b>
1. Add bot to your group as admin
2. Send <code>/connect</code> in group
3. Bot will provide connection link
4. Click link to connect in PM

<b>Connection benefits:</b>
• Manage filters from PM
• Add/delete filters remotely
• View group statistics
• Broadcast to group members

<b>Admin only features:</b>
• Only group admins can connect
• Secure connection system
• Auto-disconnect on admin removal"""