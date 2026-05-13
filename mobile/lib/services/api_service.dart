import 'dart:convert';

import 'package:http/http.dart' as http;

import '../models/estacion.dart';
import 'api_config.dart';
import 'auth_service.dart';

class UnauthorizedException implements Exception {
  const UnauthorizedException([this.message = 'Sesión expirada o inválida']);

  final String message;

  @override
  String toString() => message;
}

class ApiService {
  // Usa `baseUrl` global definido arriba
  Future<List<Estacion>> fetchEstaciones() async {
    final response = await http
        .get(Uri.parse('$apiBaseUrl/estaciones/'))
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 200) {
      final List jsonResponse = json.decode(response.body);
      return jsonResponse.map((data) => Estacion.fromJson(data)).toList();
    }
    if (response.statusCode == 401) {
      await AuthService().logout();
      throw const UnauthorizedException();
    }
    throw Exception('Error al conectar con el servidor SMAT');
  }

  Future<bool> eliminarEstacion(int id) async {
    final token = await AuthService().getToken();
    final response = await http
        .delete(
          Uri.parse('$apiBaseUrl/estaciones/$id'),
          headers: {'Authorization': 'Bearer $token'},
        )
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 401) {
      await AuthService().logout();
      throw const UnauthorizedException();
    }
    return response.statusCode == 200;
  }

  Future<bool> editarEstacion(int id, String nombre, String ubicacion) async {
    final token = await AuthService().getToken();
    final response = await http
        .put(
          Uri.parse('$apiBaseUrl/estaciones/$id'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
          body: jsonEncode({'nombre': nombre, 'ubicacion': ubicacion}),
        )
        .timeout(const Duration(seconds: 10));
    if (response.statusCode == 401) {
      await AuthService().logout();
      throw const UnauthorizedException();
    }
    return response.statusCode == 200;
  }
}

Future<bool> crearEstacion(String nombre, String ubicacion) async {
  final token = await AuthService().getToken();
  final response = await http
      .post(
        Uri.parse('$apiBaseUrl/estaciones/'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({'nombre': nombre, 'ubicacion': ubicacion}),
      )
      .timeout(const Duration(seconds: 10));
  if (response.statusCode == 401) {
    await AuthService().logout();
    throw const UnauthorizedException();
  }
  return response.statusCode == 200;
}

Future<bool> eliminarEstacion(int id) async {
  return ApiService().eliminarEstacion(id);
}

Future<bool> editarEstacion(int id, String nombre, String ubicacion) async {
  return ApiService().editarEstacion(id, nombre, ubicacion);
}
