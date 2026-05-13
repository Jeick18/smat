class Estacion {
  final int id;
  final String nombre;
  final String ubicacion;
  final double? ultimaLectura;

  Estacion({
    required this.id,
    required this.nombre,
    required this.ubicacion,
    this.ultimaLectura,
  });

  factory Estacion.fromJson(Map<String, dynamic> json) {
    return Estacion(
      id: json['id'],
      nombre: json['nombre'],
      ubicacion: json['ubicacion'],
      ultimaLectura: json['ultima_lectura'] == null
          ? null
          : (json['ultima_lectura'] as num).toDouble(),
    );
  }
}
