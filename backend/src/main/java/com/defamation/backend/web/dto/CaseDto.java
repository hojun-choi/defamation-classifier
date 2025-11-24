package com.defamation.backend.web.dto;

import com.defamation.backend.domain.Case;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.*;

import java.util.Collections;
import java.util.List;

@Getter @Setter
@AllArgsConstructor @NoArgsConstructor
@Builder
public class CaseDto {

    private Long id;
    private Long rawId;

    private String problemSituation;
    private List<String> participants;

    private List<String> caseNames;
    private String caseType;
    private Integer courtLevel;
    private String defendant;
    private Integer label;

    private String sentenceType;
    private String sentenceValue;
    private String sentenceSuspension;
    private String sentenceAdditionalOrder;
    private String sentenceReason;
    private String sentenceJudgment;

    public static CaseDto from(Case c, ObjectMapper om) {
        return CaseDto.builder()
                .id(c.getId())
                .rawId(c.getRawId())
                .problemSituation(c.getProblemSituation())
                .participants(parseList(om, c.getParticipants()))
                .caseNames(parseList(om, c.getCaseNames()))
                .caseType(c.getCaseType())
                .courtLevel(c.getCourtLevel())
                .defendant(c.getDefendant())
                .label(c.getLabel())
                .sentenceType(c.getSentenceType())
                .sentenceValue(c.getSentenceValue())
                .sentenceSuspension(c.getSentenceSuspension())
                .sentenceAdditionalOrder(c.getSentenceAdditionalOrder())
                .sentenceReason(c.getSentenceReason())
                .sentenceJudgment(c.getSentenceJudgment())
                .build();
    }

    private static List<String> parseList(ObjectMapper om, String jsonOrText) {
        if (jsonOrText == null || jsonOrText.isBlank()) return Collections.emptyList();
        try {
            return om.readValue(jsonOrText, new TypeReference<List<String>>() {});
        } catch (Exception e) {
            // 혹시 JSON이 아니라 그냥 문자열로 들어가 있으면 fallback
            return List.of(jsonOrText);
        }
    }
}
