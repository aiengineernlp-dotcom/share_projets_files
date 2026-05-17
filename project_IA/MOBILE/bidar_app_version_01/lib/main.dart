import 'package:bidar_app/views/auth/login_screen.dart';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'dart:io' show Platform;

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  if (Platform.isAndroid) {      // va voir sur Chat GTP et demander pour si la plateforme est autre que android ou meme les deux (android et une autre )
    await Firebase.initializeApp(
      options: const FirebaseOptions(   // pourquoi constant ???
        apiKey: "AIzaSyAcuRN9gL1lhf1Xc3HdefuUda86FUItvHM",
        appId: "1:840889239511:android:92bd15e2a8dff6596fed92",
        messagingSenderId: "840889239511",
        projectId: "app-bidar-version-01",
        storageBucket: 'gs://app-bidar-version-01.appspot.com',  // pour permettre que on uploade les fichier dans FIREBASE
      ),
    );
  } else {
    await Firebase.initializeApp();
  }

  runApp(const MyApp());
}


class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      //debugShowCheckedModeBanner: false,
      title: 'Flutter Demo',
      theme: ThemeData(

        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: LoginScreen(),
    );
  }
}