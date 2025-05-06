import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'dart:io';
import 'package:path_provider/path_provider.dart';

void main() {
  runApp(const MyApp());
}

// Root widget
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chat App',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
      ),
      home: const MyHomePage(title: 'Chat App'),
    );
  }
}

// Class to represent chat message
class ChatEntry {
  final String text;
  final bool isUser;

  // Get all text from chat entries
  static List<String> getAllTexts(List<ChatEntry> entries) {
    return entries.map((entry) => entry.text).toList();
  }

  ChatEntry({required this.text, required this.isUser});
} 

// Home page widget with state
class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key, required this.title});

  final String title;

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

// State class for home page
class _MyHomePageState extends State<MyHomePage> {

  TextEditingController _controller = TextEditingController();
  List<ChatEntry> _messages = [];
  
  Future<void> _sendMessage(String text) async {
    final path = await _getLocalPath();
    final file_location = '$path\\userData.csv';

    if (text.isEmpty) return;

    try{
      // Send HTTP POST request to server
      final response = await http.post(
        Uri.parse("http://localhost:5000/RAG"),
        headers: {
          "Content-Type": "application/json",
        },
        body: jsonEncode({
          "text": text,
          "messages": _messages.map((entry) => {
            "role": entry.isUser ? 'User' : 'non-user',
            "text": entry.text,
            
          }).toList(),
          "file_location": file_location,
        }),
      );

      if (response.statusCode == 200){
        // Update chat with response
        final data = jsonDecode(response.body);
        setState(() {
          _messages.insert(0, ChatEntry(text: data['original'], isUser: true));
          _messages.insert(0, ChatEntry(text: data['response'], isUser: false));
        });
      }
    }catch (e) {
      print("Error: $e");
    }

    _controller.clear();
  }

  // Show input dialog for user details
  void _showInputDialog(BuildContext context) async{
    Map<String, String>? previousData = await _readUserData();

    TextEditingController heightController = TextEditingController();
    TextEditingController weightController = TextEditingController();
    TextEditingController ageController = TextEditingController();
    String? gender = previousData?['gender'];
    
    TextEditingController waterIntakeController = TextEditingController();
    TextEditingController caloriesIntakeController = TextEditingController();
    TextEditingController sleepHoursController = TextEditingController();
    TextEditingController stepsCountController = TextEditingController();
    
    // Fill with previous data if available
    if (previousData != null) {
      heightController.text = previousData['height'] ?? '';
      weightController.text = previousData['weight'] ?? '';
      ageController.text = previousData['age'] ?? '';
      gender = previousData['gender'];
    }

    showDialog(
      context: context,
      builder: (BuildContext context){
        return AlertDialog(
          title: Text('Enter Details'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: heightController,
                decoration: InputDecoration(labelText: 'Height (cm)'),
              ),
              TextField(
                controller: weightController,
                decoration: InputDecoration(labelText: 'Weight (lbs)'),
              ),
              TextField(
                controller: ageController,
                decoration: InputDecoration(labelText: 'Age'),
              ),
              DropdownButtonFormField<String>(
                value: gender,
                items: ['Male', 'Female', 'Other', 'Prefer not to say'].map((String value) {
                  return DropdownMenuItem(
                    value: value,
                    child: Text(value),
                  );
                }).toList(),

                onChanged: (String? newValue){
                  setState(() {
                    gender = newValue;
                  });
                },
              ),
              TextField(
                controller: waterIntakeController,
                decoration: InputDecoration(labelText: 'Water Intake (oz)'),
              ),
              TextField(
                controller: caloriesIntakeController,
                decoration: InputDecoration(labelText: 'Calories Intake'),
              ),
              TextField(
                controller: sleepHoursController,
                decoration: InputDecoration(labelText: 'Sleep Hours'),
              ),
              TextField(
                controller: stepsCountController,
                decoration: InputDecoration(labelText: 'Steps Count'),
              ),
            ],
          ),
          actions: <Widget>[
            TextButton(
              child: Text('Cancel'),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
            TextButton(
              child: Text('Save'),
              onPressed: () async{
                // Make all fields required
                if (heightController.text.isEmpty || 
                    weightController.text.isEmpty || 
                    ageController.text.isEmpty || 
                    gender == null||
                    waterIntakeController.text.isEmpty || 
                    caloriesIntakeController.text.isEmpty || 
                    sleepHoursController.text.isEmpty || 
                    stepsCountController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Please fill all fields')),
                  );
                  return;
                }

                // Save user data
                await _saveUserData({
                  'height': heightController.text,
                  'weight': weightController.text,
                  'age': ageController.text,
                  'gender': gender!,
                  'waterIntake': waterIntakeController.text,
                  'caloriesIntake': caloriesIntakeController.text,
                  'sleepHours': sleepHoursController.text,
                  'stepsCount': stepsCountController.text,
              });

                Navigator.of(context).pop();
              },
            ),
          ]
        );
      }
    );
  }

  // Get local storage path to store user_data
  Future<String> _getLocalPath() async{
    final directory = await getApplicationDocumentsDirectory();
    return directory.path;
  }

  // Save user data to CSV file
  Future<void> _saveUserData(Map<String, String> data) async {
    final path = await _getLocalPath();
    final file = File('$path/userData.csv');

    final String header = 'Height (cm),Weight (lbs),Age,Gender,Water Intake (oz),Calories Intake,Sleep Hours,Steps Count\n';
    final String row = '${data['height']},${data['weight']},${data['age']},${data['gender']},${data['waterIntake']},${data['caloriesIntake']},${data['sleepHours']},${data['stepsCount']}';


    if (await file.exists()) {
      String content = await file.readAsString();
      List <String> splits = content.split('\n');
      splits.insert(1, row);
      
      String joinedContent = splits.join('\n');


      await file.writeAsString(joinedContent);
    }else{
      await file.writeAsString(header + row + '\n');
    }
  }

  // Read user data from CSV file
  Future<Map<String, String>?> _readUserData() async {
    final path = await _getLocalPath();
    print("Reading user data from: $path/userData.csv");
    final file = File('$path/userData.csv');

    if (await file.exists()){
      List<String> lines = await file.readAsLines();
      if (lines.length > 1) {
        String lastLine = lines.last;
        List<String> values = lastLine.split(',');

        return {
          'height': values[0],
          'weight': values[1],
          'age': values[2],
          'gender': values[3]
        };
      }
    }
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text(widget.title),
      ),
      body: Stack(
        children: [
          // Chat message
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Expanded(
                child: ListView.builder(
                  reverse: true,
                  itemCount: _messages.length,
                  itemBuilder: (context, index) {
                    final message = _messages[index];
                    return ChatMessage(
                      text: message.text,
                      isUser: message.isUser,
                    );
                  },
                ),
              ),
              // Message input area
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: _controller,
                        decoration: InputDecoration(
                          hintText: 'Type your message...',
                          border: OutlineInputBorder(
                            borderRadius: BorderRadius.circular(24),
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
              ),
            ],
          ),
          
          // Positioned plus button for adding user data
          Positioned(
            top: MediaQuery.of(context).size.height * 0.025,  
            right: MediaQuery.of(context).size.width * 0.01,
            child: FloatingActionButton(
              mini: true,
              child: Icon(Icons.add),
              onPressed: () => _showInputDialog(context),
            ),
          ),
        ],
      ),
    );
  }
}

// Widget to display a chat message
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