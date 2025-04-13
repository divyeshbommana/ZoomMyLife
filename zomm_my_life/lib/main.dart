import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chat App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const MyHomePage(title: 'Chat App Home Page'),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {

  TextEditingController _controller = TextEditingController();
  List<String> _messages = [];

  void _sendMessage(String text) {
    if (text.isNotEmpty) {
      setState(() {
        _messages.insert(0, text);
        _controller.clear();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children:[
            Expanded(
              child: ListView.builder(
                reverse: true,
                itemCount: _messages.length,
                itemBuilder: (context, index) {
                  return ChatMessage(
                    text: _messages[index],
                    isUser: true,
                  );
                },
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                children: [
                  // Expanded(
                  //   child: TextField(
                  //     controller: _controller,
                  //     decoration: InputDecoration(
                  //       hintText: 'Type a message',
                  //       border: OutlineInputBorder(
                  //         borderRadius: BorderRadius.circular(12.0),
                  //       ),
                  //     ),
                  //     onSubmitted: (text) {
                  //       _sendMessage(text);
                  //     },
                  //   ),
                  // ),
                  // IconButton(
                  //   icon: const Icon(Icons.send),
                  //   onPressed: () {
                  //     _sendMessage(_controller.text);
                  //   },
                  // ),
                ],
              ),
            ),  

            Container(
              padding: const EdgeInsets.all(8.0),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: 'Type your message...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(12.0),
                        ),
                      ),
                      onSubmitted: _sendMessage,
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: () => _sendMessage(_controller.text),
                  ),
                ],
              ),
            )        
          ],
        ),
      ),
    );
  }
}

class ChatMessage extends StatelessWidget {
  final String text;
  final bool isUser;

  const ChatMessage({
    super.key,
    required this.text,
    required this.isUser,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 16.0),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.7),
            padding: const EdgeInsets.all(12.0),
            decoration: BoxDecoration(
              color: isUser
                  ? Colors.blue.shade100
                  : Colors.grey.shade200,
              borderRadius: BorderRadius.circular(12.0),
            ),
            child: Text(text),
          ),
        ],
      ),
    );
  }
}