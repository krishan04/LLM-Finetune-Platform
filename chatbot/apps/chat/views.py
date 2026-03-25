from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .services import run_chat_turn


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def conversation_list(request):
    """
    GET  — list all conversations for the user (most recent first)
    POST — start a new conversation
    """
    if request.method == "GET":
        convs = request.user.conversations.all()
        return Response(ConversationSerializer(convs, many=True).data)

    conv = Conversation.objects.create(
        user=request.user,
        title=request.data.get("title", ""),
    )
    return Response(ConversationSerializer(conv).data, status=status.HTTP_201_CREATED)


@api_view(["GET", "DELETE"])
@permission_classes([IsAuthenticated])
def conversation_detail(request, pk):
    try:
        conv = request.user.conversations.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "DELETE":
        conv.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response(ConversationSerializer(conv).data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def message_list(request, pk):
    """
    GET  — return the message history for a conversation
    POST — send a message; triggers memory retrieval + LLM response
    """
    try:
        conv = request.user.conversations.get(pk=pk)
    except Conversation.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        messages = conv.messages.order_by("created_at")
        return Response(MessageSerializer(messages, many=True).data)

    # POST — run a chat turn
    user_content = request.data.get("content", "").strip()
    if not user_content:
        return Response({"detail": "content is required."}, status=status.HTTP_400_BAD_REQUEST)

    result = run_chat_turn(
        user=request.user,
        conversation=conv,
        user_content=user_content,
    )
    return Response(result, status=status.HTTP_200_OK)