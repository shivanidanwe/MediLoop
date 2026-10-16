import 'package:flutter_test/flutter_test.dart';
import 'package:mediloop/main.dart';

void main() {
  testWidgets('App starts on Splash Screen and displays app name', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MediLoopApp());

    // Verify that the app starts by displaying the app name "MediLoop".
    expect(find.text('MediLoop'), findsOneWidget);

    // Let the splash timer and animations settle so no timers remain pending
    await tester.pumpAndSettle(const Duration(seconds: 3));
  });
}
