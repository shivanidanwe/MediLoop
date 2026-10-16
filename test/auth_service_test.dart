import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:mediloop/services/auth_service.dart';
import 'package:mediloop/models/user_model.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('AuthService Tests', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
    });

    test('login returns success and stores token on 200 OK', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.endsWith('/auth/login')) {
          return http.Response(
            jsonEncode({
              'access_token': 'fake_jwt_token_123',
              'token_type': 'bearer',
              'user': {
                'id': 1,
                'full_name': 'Test User',
                'email': 'test@example.com',
                'mobile_number': '1234567890',
                'gender': 'MALE',
                'date_of_birth': '1995-01-01',
              }
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('Not Found', 404);
      });

      final authService = AuthService(client: mockClient);
      final result = await authService.login('test@example.com', 'password123');

      expect(result['success'], true);
      expect(result['token'], 'fake_jwt_token_123');
      expect((result['user'] as UserModel).name, 'Test User');

      final storedToken = await authService.getToken();
      expect(storedToken, 'fake_jwt_token_123');
      expect(await authService.isLoggedIn(), true);
    });

    test('login returns failure message on 401 Unauthorized', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({'detail': 'Incorrect email or password'}),
          401,
          headers: {'content-type': 'application/json'},
        );
      });

      final authService = AuthService(client: mockClient);
      final result = await authService.login('wrong@example.com', 'wrongpass');

      expect(result['success'], false);
      expect(result['message'], 'Incorrect email or password');
      expect(await authService.isLoggedIn(), false);
    });

    test('logout clears stored token and session', () async {
      SharedPreferences.setMockInitialValues({
        'auth_token': 'stored_token_abc',
      });

      final authService = AuthService();
      expect(await authService.isLoggedIn(), true);

      await authService.logout();
      expect(await authService.isLoggedIn(), false);
      expect(await authService.getToken(), null);
    });
  });
}
