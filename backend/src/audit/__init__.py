"""Módulo de auditoría — specs/016-auditoria.

Registra automáticamente toda escritura exitosa (`AuditMiddleware`) y expone
su lectura a organizadores (`GET /admin/audit-log`). No participa del modelo
de dominio de negocio (`League/Team/Player/Match/MatchEvent`); solo referencia
`User` como actor opcional.
"""
