FROM alpine:3.24 AS base_ssh

RUN apk add --no-cache openssh-server \
    && adduser -D -s /bin/sh tunel_devel \
    && passwd -d tunel_devel \
    && mkdir -p /home/tunel_devel/.ssh \
    && chmod 700 /home/tunel_devel/.ssh

COPY chave_tunel_devel.pub /home/tunel_devel/.ssh/authorized_keys

RUN chown -R tunel_devel:tunel_devel /home/tunel_devel/.ssh \
    && chmod 600 /home/tunel_devel/.ssh/authorized_keys

FROM cloudflare/cloudflared:latest

COPY --from=base_ssh /usr/ /usr/
COPY --from=base_ssh /bin/ /usr/bin/
COPY --from=base_ssh /sbin/ /usr/sbin/
COPY --from=base_ssh /lib/ /usr/lib/
COPY --from=base_ssh /etc/ /etc/
COPY --from=base_ssh /home/ /home/

USER root

ENTRYPOINT ["/bin/sh", "-c"]
CMD ["mkdir -p /run/sshd /var/empty && chmod 755 /var/empty && ssh-keygen -A && /usr/sbin/sshd -p 2222 -o PasswordAuthentication=no -o KbdInteractiveAuthentication=no -o PermitRootLogin=no -o AllowTcpForwarding=local -o PermitOpen=llm.example.invalid:9001 && exec cloudflared tunnel --url ssh://127.0.0.1:2222"]