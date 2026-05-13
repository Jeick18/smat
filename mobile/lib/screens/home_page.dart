import 'package:flutter/material.dart';

import '../models/estacion.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';
import 'add_estacion.dart';
import 'login_screen.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});
  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  late Future<List<Estacion>> futureEstaciones;
  final ApiService apiService = ApiService();
  bool _redirectingToLogin = false;

  @override
  void initState() {
    super.initState();
    futureEstaciones = ApiService().fetchEstaciones();
  }

  Future<void> _refreshData() async {
    setState(() {
      futureEstaciones = ApiService().fetchEstaciones();
    });
    await futureEstaciones;
  }

  void _irALogin() {
    if (_redirectingToLogin) {
      return;
    }
    _redirectingToLogin = true;
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (!mounted) return;
      Navigator.pushAndRemoveUntil(
        context,
        MaterialPageRoute(builder: (context) => const LoginScreen()),
        (route) => false,
      );
    });
  }

  Color _colorParaLectura(double? lectura) {
    if (lectura == null) {
      return Colors.indigo;
    }
    return lectura > 50 ? Colors.red : Colors.green;
  }

  void _mostrarDialogoEdicion(Estacion estacion) {
    final nombreCtrl = TextEditingController(text: estacion.nombre);
    final ubicacionCtrl = TextEditingController(text: estacion.ubicacion);
    bool isSaving = false;

    showDialog(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Editar Estación'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nombreCtrl,
                decoration: const InputDecoration(labelText: 'Nombre'),
              ),
              TextField(
                controller: ubicacionCtrl,
                decoration: const InputDecoration(labelText: 'Ubicación'),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: isSaving ? null : () => Navigator.pop(dialogContext),
              child: const Text('Cancelar'),
            ),
            ElevatedButton(
              onPressed: isSaving
                  ? null
                  : () async {
                      setDialogState(() => isSaving = true);
                      try {
                        final ok = await apiService.editarEstacion(
                          estacion.id,
                          nombreCtrl.text,
                          ubicacionCtrl.text,
                        );
                        if (!mounted) return;
                        if (ok) {
                          Navigator.pop(dialogContext);
                          await _refreshData();
                        }
                      } on UnauthorizedException {
                        if (!mounted) return;
                        Navigator.pop(dialogContext);
                        _irALogin();
                      } finally {
                        if (mounted && Navigator.of(dialogContext).canPop()) {
                          setDialogState(() => isSaving = false);
                        }
                      }
                    },
              child: isSaving
                  ? const SizedBox(
                      height: 18,
                      width: 18,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('Guardar'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Estaciones SMAT'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              final ctx = context;
              await AuthService().logout();
              if (!mounted) return;
              Navigator.pushAndRemoveUntil(
                ctx,
                MaterialPageRoute(builder: (context) => const LoginScreen()),
                (route) => false,
              );
            },
            tooltip: 'Salir',
          ),
        ],
      ),
      body: FutureBuilder<List<Estacion>>(
        future: futureEstaciones,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(color: Color(0xFF10B981)),
            );
          } else if (snapshot.hasError) {
            if (snapshot.error is UnauthorizedException) {
              _irALogin();
              return const Center(child: CircularProgressIndicator());
            }
            return const Center(child: Text('❌ Error de conexión'));
          } else {
            final estaciones = snapshot.data ?? [];
            if (estaciones.isEmpty) {
              return RefreshIndicator(
                onRefresh: _refreshData,
                child: ListView(
                  physics: AlwaysScrollableScrollPhysics(),
                  children: const [
                    SizedBox(height: 220),
                    Center(child: Text('No hay estaciones registradas')),
                  ],
                ),
              );
            }
            return RefreshIndicator(
              onRefresh: _refreshData,
              child: ListView.builder(
                physics: const AlwaysScrollableScrollPhysics(),
                itemCount: estaciones.length,
                itemBuilder: (context, index) {
                  final est = estaciones[index];
                  return Dismissible(
                    key: Key(est.id.toString()),
                    direction: DismissDirection.endToStart,
                    background: Container(
                      color: Colors.red,
                      alignment: Alignment.centerRight,
                      padding: const EdgeInsets.only(right: 20),
                      child: const Icon(Icons.delete, color: Colors.white),
                    ),
                    confirmDismiss: (direction) async {
                      try {
                        final ok = await apiService.eliminarEstacion(est.id);
                        if (!mounted) return false;
                        if (ok) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('${est.nombre} eliminada')),
                          );
                          await _refreshData();
                          return true;
                        }
                        ScaffoldMessenger.of(context).showSnackBar(
                          SnackBar(
                            content: Text('No se pudo eliminar ${est.nombre}'),
                          ),
                        );
                        return false;
                      } on UnauthorizedException {
                        if (!mounted) return false;
                        _irALogin();
                        return false;
                      }
                    },
                    child: ListTile(
                      leading: Icon(
                        Icons.satellite_alt,
                        color: _colorParaLectura(est.ultimaLectura),
                      ),
                      title: Text(est.nombre),
                      subtitle: Text(
                        est.ultimaLectura == null
                            ? est.ubicacion
                            : '${est.ubicacion} · Última lectura: ${est.ultimaLectura!.toStringAsFixed(1)}',
                      ),
                      onTap: () => _mostrarDialogoEdicion(est),
                    ),
                  );
                },
              ),
            );
          }
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final result = await Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => AddEstacionScreen()),
          );
          if (result == true) {
            _refreshData();
          }
        },
        backgroundColor: Colors.indigo,
        foregroundColor: Colors.white,
        child: const Icon(Icons.add),
      ),
    );
  }
}
