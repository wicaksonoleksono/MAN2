class HikEvent {
  final String cardNo;
  final String? employeeNo;
  final DateTime dateTime;
  final int serialNo;

  HikEvent({
    required this.cardNo,
    this.employeeNo,
    required this.dateTime,
    required this.serialNo,
  });

  @override
  String toString() =>
      'HikEvent(card=$cardNo, serial=$serialNo, time=$dateTime)';
}

class DeviceInfo {
  final String deviceName;
  final String model;
  final String serialNumber;
  final String firmwareVersion;

  DeviceInfo({
    required this.deviceName,
    required this.model,
    required this.serialNumber,
    required this.firmwareVersion,
  });

  @override
  String toString() => '$deviceName ($model)';
}
